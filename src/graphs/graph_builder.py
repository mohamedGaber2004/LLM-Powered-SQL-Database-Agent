from src.LLMs.groq_gpt_oss import LLM
from src.tools.database_tool import execute_query , generate_sql_query

from langgraph.graph import StateGraph , START , END
from pydantic import BaseModel
from langgraph.prebuilt import ToolNode , tools_condition
from langchain_core.messages import HumanMessage

class SQLAgent(BaseModel):
    str_Query : str
    sql_Query : str

class GraphBuilder :
    def __init__(self):
        self.llm = LLM().get_llm().bind_tools([generate_sql_query])
        self.graph = None
        self.graph_png = None

    def sql_agent(self,state:SQLAgent)->dict:
        response = self.llm.invoke(state.str_Query)
        print(response)
        state.sql_Query = response
        return {"sql_Query":state.sql_Query}


    def build_graph(self):
        graph = StateGraph(SQLAgent)

        graph.add_node("sql_agent",self.sql_agent)
        graph.add_node("generate_sql_query",ToolNode([generate_sql_query]))

        graph.add_edge(START,"sql_agent")
        graph.add_conditional_edges("sql_agent",tools_condition)
        graph.add_edge("generate_sql_query", "sql_agent")
        graph.add_edge("sql_agent",END)

        self.graph = graph.compile()
        self.graph_png = self.graph().get_graph().draw_mermaid_png() 

    
    def run(self, user_query: str):
        self.build_graph()

        return self.graph.invoke({
            "messages": [HumanMessage(content=user_query)]
        })




