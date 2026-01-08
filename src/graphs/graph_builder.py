from src.LLMs.groq_gpt_oss import LLM
from src.tools.database_tool import execute_query , generate_sql_query

from langgraph.graph import StateGraph , START , END
from pydantic import BaseModel
from langgraph.prebuilt import ToolNode , tools_condition
from langchain_core.messages import HumanMessage
from langchain_core.messages import BaseMessage
from typing import List

class SQLAgent(BaseModel):
    messages: List[BaseMessage]
    sql_Query: str | None = None

class GraphBuilder :
    def __init__(self):
        self.llm = LLM().get_llm().bind_tools([generate_sql_query])
        self.tool_node = ToolNode([generate_sql_query])
        self.graph = None
        self.graph_png = None

    def llm_node(self, state: SQLAgent):
        response = self.llm.invoke(state.messages)
        return {"messages": state.messages + [response]}


    def extract_sql(self, state: SQLAgent):
        last_message = state.messages[-1]
        return {"sql_Query": last_message.content}

    
    def build_graph(self):
        graph = StateGraph(SQLAgent)

        graph.add_node("llm", self.llm_node)
        graph.add_node("tools", self.tool_node)
        graph.add_node("extract_sql", self.extract_sql)

        graph.add_edge(START, "llm")
        graph.add_conditional_edges("llm", tools_condition)
        graph.add_edge("tools", "extract_sql")
        graph.add_edge("extract_sql", END)

        self.graph = graph.compile()

    
    def run(self, user_query: str):
        self.build_graph()
        result = self.graph.invoke({
            "messages": [HumanMessage(content=user_query)]
        })
        return result["sql_Query"]




