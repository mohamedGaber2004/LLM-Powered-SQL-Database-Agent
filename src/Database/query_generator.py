import os , re
import sqlparse
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from langchain_core.messages import HumanMessage , SystemMessage

from src.Database.database import engine , get_schema
from src.LLMs.groq_gpt_oss import LLM

llm = LLM()
llm = llm.get_llm()

load_dotenv()



def clean_sql_output(response_text):
    """Removes markdown formating and extracts the raw SQL query."""
    clean_query = re.sub(r"```sql\n(.*?)\n```", r"\1", response_text, flags=re.DOTALL)
    sql_match = re.search(r"SELECT .*?;", clean_query, re.DOTALL | re.IGNORECASE)
    return sql_match.group(0) if sql_match else clean_query.strip()


def validate_sql_query(sql_query) :
    """Validate the SQL query syntax before execution."""
    try : 
        parsed = sqlparse.parse(sql_query)
        if not parsed :
            return False , "Invalid SQL syntax."
        return True , None
    except Exception as e :
        return False , str(e)
    

def generate_sql_query(nl_query):
    """Converts natural language query to an otimized SQL query."""
    schema = get_schema()

    schema_text = "\n".join([f"{table}: {','.join(columns)}" for table , columns in schema.items()])
    prompt = f"""
    You are an SQL expert.Convert the following natural language query into an optimized MySQL query.
    Ensure : 
    - Proper use of INDEXING where applicable.
    - Use of efficient JOINS instead of nasted queries.
    - Use GROUP BY when aggregation are needed.
    - Ensure SQL is valid and optimized for execution.

    Database Schema:
    {schema_text}

    User Request: {nl_query}

    SQL Query:"""

    try : 
        response = llm.invoke([
            SystemMessage(content="You are an SQL optimization expert."),
            HumanMessage(content=prompt)
        ])
        raw_sql_query = response.content

        clean_query = clean_sql_output(raw_sql_query)
        return clean_query
    
    except Exception as e :
        print(f"Error generating SQL query :{e}")
        return None
    

def suggest_index (sql_query) : 
    """Suggest indexes for the executed sql query."""
    try : 
        with engine._connect() as connection : 
            explain_query = f"EXPLAIN {sql_query}"
            result = connection.execute(text(explain_query))
            execution_plan = result.fetchall()

        print("\nQuery Execution Plan:\n")
        for row in execution_plan : 
            print(row)

        return "Consider adding an index on frequently used WHERE conditions."

    except Exception as e :
        return f"Couldn't Generate Execution plan :{e}"
    


def execute_query(sql_query) : 
    """Executes a validated and optimized SQL Query"""
    is_valid , error_msg = validate_sql_query(sql_query)
    if not is_valid : 
        print(f"SQL Validation Error:{error_msg}")
        return None
    
    try : 
        with engine.connect() as connection : 
            result = connection.execute(text(sql_query))
            fetched_results = result.fetchall()

        index_suggestion = suggest_index(sql_query)

        return {"results":fetched_results,"optimization_tips":index_suggestion}
    except SQLAlchemyError as e : 
        print(f"Database Execution Error :{str(e)}")
        return None
    



if __name__ == "__main__" : 
    user_input = input("Enter you natural language query: ")
    sql_query = generate_sql_query(user_input)

    if sql_query : 
        print(f"\nGenerated SQL Query:\n{sql_query}")

        execution_results = execute_query(sql_query)
        if execution_results : 
            for row in execution_results['results'] : 
                print(row)

        else : 
            print("No results found")

    else :
        print("Failed to generate a valid SQL query") 
