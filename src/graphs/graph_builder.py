# src/graphs/graph_builder.py
import json
from typing import List
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, BaseMessage

from langgraph.graph import StateGraph, START, END

from src.LLMs.groq_gpt_oss import LLM
from src.tools.database_tool import generate_sql_query, execute_query

class SQLAgent(BaseModel):
    messages: List[BaseMessage] = []
    sql_Query: str | None = None
    res_Query: str | None = None
    error: str | None = None

class GraphBuilder:
    def __init__(self):
        self.llm = LLM().get_llm()
        self.graph = None
        self.graph_png = None

    def llm_node(self, state: SQLAgent):
        """LLM generates SQL from the user query"""
        try:
            if not state.messages:
                return {"error": "No messages provided"}
            
            user_query = state.messages[-1].content
            sql = generate_sql_query(user_query)
            
            if not sql:
                return {"error": "Failed to generate SQL", "sql_Query": None}
            
            # Return the SQL in the state
            return {"sql_Query": sql}
        except Exception as e:
            return {"error": str(e), "sql_Query": None}

    def extract_sql(self, state: SQLAgent):
        """Extract SQL from state"""
        if state.error:
            return {}
        
        if state.sql_Query:
            return {}  # SQL already in state
        
        return {"error": "No SQL query in state"}

    def execute_sql_node(self, state: SQLAgent):
        """Execute the SQL query and return results"""
        # Check for errors from previous steps
        if state.error:
            return {}
        
        sql = state.sql_Query
        if not sql:
            return {"error": "No SQL query to execute", "res_Query": None}

        try:
            result = execute_query(sql)
            if result is None:
                return {
                    "error": "Query execution failed",
                    "res_Query": json.dumps({"error": "Execution failed"})
                }
            
            # Serialize results properly
            res_json = json.dumps({
                "results": [dict(row._mapping) for row in result.get("results", [])],
                "optimization_tips": result.get("optimization_tips"),
                "status": "success"
            }, default=str)
            
            return {"res_Query": res_json}
            
        except Exception as e:
            error_msg = f"Execution error: {str(e)}"
            return {
                "error": error_msg,
                "res_Query": json.dumps({"error": error_msg})
            }

    def extract_res(self, state: SQLAgent):
        """Final result extraction"""
        if state.error:
            return {"res_Query": json.dumps({"error": state.error})}
        return {}

    def build_graph(self):
        """Build the execution graph"""
        graph = StateGraph(SQLAgent)

        # Add nodes - simplified without tool node
        graph.add_node("llm", self.llm_node)
        graph.add_node("extract_sql", self.extract_sql)
        graph.add_node("execute_sql", self.execute_sql_node)
        graph.add_node("extract_res", self.extract_res)

        # Define edges - direct flow without tool routing
        graph.add_edge(START, "llm")
        graph.add_edge("llm", "extract_sql")
        graph.add_edge("extract_sql", "execute_sql")
        graph.add_edge("execute_sql", "extract_res")
        graph.add_edge("extract_res", END)

        self.graph = graph.compile()
        
        # Optional visualization
        try:
            self.graph_png = self.graph.get_graph().draw_mermaid_png()
        except Exception:
            self.graph_png = None

    def run(self, user_query: str, execute: bool = True):
        """
        Execute the query pipeline.
        
        Args:
            user_query: Natural language query
            execute: If True, execute SQL and return results. If False, only generate SQL.
        
        Returns:
            JSON string with results or error, or SQL string if execute=False
        """
        if not self.graph:
            self.build_graph()
        
        if execute:
            # Full execution: generate SQL and run it
            result = self.graph.invoke({
                "messages": [HumanMessage(content=user_query)]
            })
            
            # Return results or SQL or error
            if isinstance(result, dict):
                if result.get("res_Query"):
                    return result["res_Query"]
                elif result.get("sql_Query"):
                    return json.dumps({
                        "sql": result["sql_Query"],
                        "status": "generated_only"
                    })
                elif result.get("error"):
                    return json.dumps({"error": result["error"]})
            
            return json.dumps({"error": "Unknown execution error"})
        
        else:
            # SQL generation only
            try:
                sql = generate_sql_query(user_query)
                return sql if sql else "Failed to generate SQL"
            except Exception as e:
                return f"Error: {str(e)}"