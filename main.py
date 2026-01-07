from fastapi import FastAPI
from pydantic import BaseModel
from src.Database.query_generator import generate_sql_query , execute_query

app = FastAPI()

class QueryRequest(BaseModel):
    query : str


@app.post("/generate_sql/")
def generate_sql(payload: dict):
    prompt = payload["prompt"]
    sql = generate_sql_query(prompt)
    return {"sql": sql}



@app.post("/execute_sql/")
def execute_sql(payload: dict):
    query = payload["query"]
    results, tips = execute_query(query)
    return {
        "results": results,
        "optimization_tips": tips
    }


if __name__ == "__main__" : 
    import uvicorn
    uvicorn.run(app,host="127.0.0.1",port=8000)