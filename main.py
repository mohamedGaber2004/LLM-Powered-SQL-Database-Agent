from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from src.graphs.graph_builder import GraphBuilder
from src.tools.database_tool import execute_query

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI SQL Query Generator API",
    description="Generate and execute SQL queries using natural language",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize graph builder
graph = GraphBuilder()


# Pydantic models
class GenerateSQLRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Natural language query")
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "Show me all users who registered in the last 30 days"
            }
        }


class ExecuteSQLRequest(BaseModel):
    query: str = Field(..., min_length=1, description="SQL query to execute")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "SELECT * FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY);"
            }
        }


class SQLResponse(BaseModel):
    sql_query: str
    status: str = "success"


class ExecutionResponse(BaseModel):
    results: List[Dict[str, Any]]
    optimization_tips: str
    row_count: int
    query: str
    status: str = "success"


class ErrorResponse(BaseModel):
    detail: str
    status: str = "error"


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status": "error"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "status": "error"}
    )


# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "AI SQL Generator"}


# Generate SQL endpoint
@app.post(
    "/generate_sql/",
    response_model=SQLResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate SQL from natural language"
)
def generate_sql(payload: GenerateSQLRequest):
    """
    Generate SQL query from natural language prompt.
    
    - **prompt**: Natural language description of desired query
    
    Returns the generated SQL query string.
    """
    try:
        logger.info(f"Generating SQL for prompt: {payload.prompt}")
        
        sql = graph.run(payload.prompt, execute=False)
        
        if not sql or sql.startswith("Error") or sql.startswith("Failed"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to generate valid SQL: {sql}"
            )
        
        logger.info(f"Generated SQL: {sql}")
        return SQLResponse(sql_query=sql, status="success")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating SQL: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SQL generation failed: {str(e)}"
        )


# Execute SQL endpoint
@app.post(
    "/execute_sql/",
    response_model=ExecutionResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute SQL query"
)
def execute_sql(payload: ExecuteSQLRequest):
    """
    Execute a SQL query and return results with optimization tips.
    
    - **query**: Valid SQL query to execute
    
    Returns query results, optimization tips, and row count.
    """
    try:
        logger.info(f"Executing SQL: {payload.query}")
        
        result = execute_query(payload.query)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SQL execution failed. Check query syntax and database connection."
            )
        
        rows = result.get("results", [])
        
        # Serialize rows
        try:
            serialized_rows = [dict(row._mapping) for row in rows]
        except AttributeError:
            # Handle case where rows are already dicts
            serialized_rows = rows if isinstance(rows, list) else []
        
        response = ExecutionResponse(
            results=serialized_rows,
            optimization_tips=result.get("optimization_tips", "No optimization tips available"),
            row_count=len(serialized_rows),
            query=payload.query,
            status="success"
        )
        
        logger.info(f"Query executed successfully. Returned {len(serialized_rows)} rows")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing SQL: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SQL execution failed: {str(e)}"
        )


# Combined endpoint: generate and execute in one call
@app.post(
    "/query/",
    response_model=ExecutionResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate and execute SQL in one call"
)
def query_database(payload: GenerateSQLRequest):
    """
    Generate SQL from natural language and execute it in one call.
    
    - **prompt**: Natural language description of desired query
    
    Returns query results, the generated SQL, and optimization tips.
    """
    try:
        logger.info(f"Processing query: {payload.prompt}")
        
        # Generate SQL
        sql = graph.run(payload.prompt, execute=False)
        
        if not sql or sql.startswith("Error") or sql.startswith("Failed"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to generate valid SQL: {sql}"
            )
        
        # Execute SQL
        result = execute_query(sql)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SQL execution failed"
            )
        
        rows = result.get("results", [])
        
        try:
            serialized_rows = [dict(row._mapping) for row in rows]
        except AttributeError:
            serialized_rows = rows if isinstance(rows, list) else []
        
        return ExecutionResponse(
            results=serialized_rows,
            optimization_tips=result.get("optimization_tips", "No optimization tips available"),
            row_count=len(serialized_rows),
            query=sql,
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in query pipeline: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query pipeline failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )