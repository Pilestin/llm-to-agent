from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_openai import ChatOpenAI
import os 

from dotenv import load_dotenv
load_dotenv()

your_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o-mini", api_key=your_key, organization="org-Zrtdb6pB3tDsQge2IljFR48m")

def chatbot(state: MessagesState):
    response = llm.invoke(state["messages"])

    return {
        "messages": [response]
    }

graph = StateGraph(MessagesState)

graph.add_node("chatbot", chatbot)

graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

app = graph.compile()

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    result = app.invoke({
        "messages": [
            {
                "role": "user",
                "content": user_input
            }
        ]
    })

    print("AI:", result["messages"][-1].content)