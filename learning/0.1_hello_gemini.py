from langgraph.graph import StateGraph, MessagesState, START, END
from langchain.chat_models import init_chat_model
import os 
from dotenv import load_dotenv

# Çevresel değişkenleri yükle
load_dotenv()

# 1. Modeli Başlatma (Yeni Standart)
# Bu yöntem, model sağlayıcısını (google_genai) ve model ismini ayırır.
llm = init_chat_model(
    "gemini-1.5-flash",
    model_provider="google_genai",
    api_key=os.getenv("GOOGLE_API_KEY")
)

# 2. Node Tanımı
def chatbot(state: MessagesState):
    # init_chat_model ile oluşturulan llm objesi invoke edilebilir
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# 3. Grafiği Kurma
workflow = StateGraph(MessagesState)
workflow.add_node("agent", chatbot)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

# 4. Derleme
app = workflow.compile()

# Mesaj geçmişini döngü dışında tut
chat_history = []

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    # Yeni mesajı geçmişe ekle
    chat_history.append({"role": "user", "content": user_input})

    # Tüm geçmişi gönder
    result = app.invoke({"messages": chat_history})

    # AI yanıtını al ve geçmişe ekle
    ai_response = result["messages"][-1]
    chat_history.append(ai_response)

    print("AI:", ai_response.content)