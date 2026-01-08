generate_sql_prompt = """
You are an SQL expert. Convert the following natural language query into an optimized MySQL query.

Requirements:
- Only return valid SQL code ending with a semicolon (;)
- Do NOT include comments, markdown, or index hints
- Use proper JOINs instead of nested queries
- Use GROUP BY for aggregations when needed
- Optimize for performance using indexes where applicable
- Return only SQL code, no explanations

Database Schema:
{schema_text}

User Request: {nl_query}

SQL Query:
"""

