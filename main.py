from fastapi import FastAPI

from src.graphs.graph_builder import GraphBuilder


app = FastAPI()
graph = GraphBuilder()


@app.post("/generate_sql/")
def generate_sql(payload: dict):
    prompt = payload["prompt"]
    sql = graph.run(prompt)
    sql = sql
    return {"sql_Query": sql}


if __name__ == "__main__" : 
    import uvicorn
    uvicorn.run(app,host="127.0.0.1",port=8000)