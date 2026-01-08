import re
import sqlparse
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate

from src.Database.database import DataBase
from Config.config import engine
from src.LLMs.groq_gpt_oss import LLM
from src.prompts.generate_sql_prompt import generate_sql_prompt

load_dotenv()

# Initialize once
llm = LLM().get_llm()
database_schema = DataBase().get_schema()


def clean_sql_output(response_text: str) -> str:
    """Clean LLM output to extract valid SQL"""
    if not response_text:
        return ""
    
    # Remove markdown code blocks
    clean = re.sub(r"```sql\s*", "", response_text)
    clean = re.sub(r"```\s*", "", clean)
    
    # Remove comments
    clean = re.sub(r"--.*", "", clean)
    clean = re.sub(r"/\*[\s\S]*?\*/", " ", clean)
    
    # Remove index hints (MySQL specific)
    clean = re.sub(r"\bUSE\s+INDEX\s*\([^)]+\)", " ", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\bFORCE\s+INDEX\s*\([^)]+\)", " ", clean, flags=re.IGNORECASE)
    
    # Normalize whitespace
    clean = re.sub(r"\s+", " ", clean).strip()
    
    # Extract first SQL statement
    match = re.search(
        r"((?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|WITH)\b.*?;)",
        clean,
        flags=re.IGNORECASE | re.DOTALL
    )
    
    if match:
        return match.group(1).strip()
    
    # If no semicolon found, try to add it
    if clean and not clean.endswith(";"):
        clean += ";"
    
    return clean


def validate_sql_query(sql_query: str) -> tuple[bool, str | None]:
    """
    Validate SQL syntax using basic checks and sqlparse.
    
    Returns:
        (is_valid, error_message)
    """
    if not sql_query or not isinstance(sql_query, str):
        return False, "Empty or non-string SQL query"

    sql = sql_query.strip()
    
    # Must end with semicolon
    if not sql.endswith(";"):
        return False, "SQL must end with a semicolon"
    
    # Must start with valid SQL verb
    if not re.match(
        r"^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|WITH)\b",
        sql,
        flags=re.IGNORECASE
    ):
        return False, "SQL must start with a valid statement (SELECT/INSERT/UPDATE/DELETE/etc.)"
    
    # Parse with sqlparse
    try:
        parsed = sqlparse.parse(sql)
        if not parsed or len(parsed) == 0:
            return False, "Invalid SQL syntax (sqlparse failed to parse)"
        
        # Check for balanced parentheses
        if sql.count("(") != sql.count(")"):
            return False, "Unbalanced parentheses in SQL query"
            
    except Exception as e:
        return False, f"SQL parsing error: {str(e)}"
    
    return True, None


def generate_sql_query(nl_query: str) -> str | None:
    """
    Convert natural language to optimized SQL using LLM.
    
    Args:
        nl_query: Natural language query description
        
    Returns:
        Clean SQL string or None if generation fails
    """
    # Format schema for prompt
    schema_text = "\n".join([
        f"Table: {table}\n  Columns: {', '.join(columns)}"
        for table, columns in database_schema.items()
    ])
    
    # Build prompt
    prompt = PromptTemplate.from_template(generate_sql_prompt).format(
        schema_text=schema_text,
        nl_query=nl_query
    )

    try:
        response = llm.invoke([
            SystemMessage(content="You are an SQL optimization expert. Generate only valid MySQL queries."),
            HumanMessage(content=prompt)
        ])
        
        raw_sql = response.content
        clean_sql = clean_sql_output(raw_sql)
        
        # Validate before returning
        is_valid, error = validate_sql_query(clean_sql)
        if not is_valid:
            print(f"Generated SQL failed validation: {error}")
            print(f"SQL: {clean_sql}")
            return None
        
        return clean_sql
        
    except Exception as e:
        print(f"Error generating SQL query: {e}")
        return None


def suggest_index(sql_query: str) -> str:
    """
    Provide index suggestions based on EXPLAIN output.
    
    Args:
        sql_query: Valid SQL SELECT query
        
    Returns:
        Index suggestion string
    """
    try:
        # Only run EXPLAIN on SELECT queries
        if not sql_query.strip().upper().startswith("SELECT"):
            return "Index suggestions only available for SELECT queries"
        
        with engine.connect() as connection:
            explain_query = f"EXPLAIN {sql_query}"
            result = connection.execute(text(explain_query))
            plan = result.fetchall()
        
        suggestions = []
        print("\n=== Query Execution Plan ===")
        for row in plan:
            print(row)
            # Analyze the plan (simplified)
            row_dict = dict(row._mapping)
            if row_dict.get('type') == 'ALL':
                table = row_dict.get('table')
                suggestions.append(f"Consider adding index on table '{table}' (full table scan detected)")
        
        if suggestions:
            return "\n".join(suggestions)
        
        return "Query plan looks optimized. No immediate index suggestions."
        
    except Exception as e:
        return f"Couldn't generate execution plan: {str(e)}"


def execute_query(sql_query: str) -> dict | None:
    """
    Execute validated SQL query and return results with optimization tips.
    
    Args:
        sql_query: Valid SQL query string
        
    Returns:
        Dict with 'results' and 'optimization_tips' keys, or None on error
    """
    # Validate first
    is_valid, error_msg = validate_sql_query(sql_query)
    if not is_valid:
        print(f"❌ SQL Validation Error: {error_msg}")
        print(f"Query: {sql_query}")
        return None

    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            
            # Check if query returns rows
            if result.returns_rows:
                rows = result.fetchall()
            else:
                # For INSERT/UPDATE/DELETE, get rowcount
                rows = [{"affected_rows": result.rowcount}]
            
            # Commit if needed (for write operations)
            if not sql_query.strip().upper().startswith("SELECT"):
                connection.commit()
        
        # Get optimization tips for SELECT queries
        index_tip = suggest_index(sql_query) if sql_query.strip().upper().startswith("SELECT") else "N/A for non-SELECT queries"
        
        return {
            "results": rows,
            "optimization_tips": index_tip,
            "query": sql_query
        }
        
    except SQLAlchemyError as e:
        print(f"❌ Database Execution Error: {e}")
        print(f"Query: {sql_query}")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return None