from langchain_ollama import ChatOllama

# Toollar 
from tools.datetime_tools import get_current_time

def get_llm():
    llm =  ChatOllama(
        model="qwen3:8b",
        temperature=0,
    )
    
    tools = [
        get_current_time
    ]
    
    llm_with_tools = llm.bind_tools(tools)
    
    return llm_with_tools