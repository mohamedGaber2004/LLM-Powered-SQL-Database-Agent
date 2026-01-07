from langchain_groq import ChatGroq
from dotenv import load_dotenv 

load_dotenv()



class LLM : 
    def __init__(self):
        self.llm = ChatGroq(model="openai/gpt-oss-120b")


    def get_llm (self):
        return self.llm