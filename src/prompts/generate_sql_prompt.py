generate_sql_prompt = """
    You are an SQL expert.Convert the following natural language query into an optimized MySQL query.
    Ensure : 
    - Proper use of INDEXING where applicable.
    - Use of efficient JOINS instead of nasted queries.
    - Use GROUP BY when aggregation are needed.
    - Ensure SQL is valid and optimized for execution.
    - Return Only SQL code without any additional text.

    Database Schema:
    {schema_text}

    User Request: {nl_query}

    SQL Query:"""