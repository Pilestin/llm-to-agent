"""
KONU: Memory & Checkpointer
=============================
3_calculator.py'deki ReAct agent'ın üzerine MemorySaver ekliyoruz.

FARK:
  3_calculator.py → her invoke() bağımsız, geçmiş yok
  5_memory.py     → aynı thread_id ile invoke() yapılırsa geçmiş korunuyor

TEMEL KAVRAMLAR:
  - MemorySaver   : Konuşma geçmişini RAM'de tutar (production'da SqliteSaver/PostgresSaver)
  - thread_id     : Konuşma kimliği. Aynı id = aynı hafıza. Farklı id = sıfırdan başlar.
  - config        : Her invoke()'a verilen, hangi thread'de çalışacağını söyleyen dict.
"""

from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain.messages import SystemMessage, HumanMessage, AnyMessage
from langchain.messages import ToolMessage
from typing_extensions import TypedDict, Annotated
from typing import Literal
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver  # <-- YENİ

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
model = ChatOllama(model="qwen3:8b", temperature=0)

# ---------------------------------------------------------------------------
# Tools (3_calculator.py ile aynı)
# ---------------------------------------------------------------------------
@tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b."""
    return a * b

@tool
def add(a: int, b: int) -> int:
    """Add a and b."""
    return a + b

@tool
def divide(a: int, b: int) -> float:
    """Divide a by b."""
    return a / b

tools = [add, multiply, divide]
tools_by_name = {t.name: t for t in tools}
model_with_tools = model.bind_tools(tools)

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------
def llm_call(state: AgentState):
    return {
        "messages": [
            model_with_tools.invoke(
                [SystemMessage(content="You are a helpful math assistant.")] + state["messages"]
            )
        ]
    }

def tool_node(state: AgentState):
    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=str(observation), tool_call_id=tool_call["id"]))
    return {"messages": result}

def should_continue(state: AgentState) -> Literal["tool_node", "__end__"]:
    if state["messages"][-1].tool_calls:
        return "tool_node"
    return "__end__"

# ---------------------------------------------------------------------------
# Graph — 3_calculator.py ile aynı yapı, tek fark: checkpointer
# ---------------------------------------------------------------------------
builder = StateGraph(AgentState)
builder.add_node("llm_call", llm_call)
builder.add_node("tool_node", tool_node)
builder.add_edge(START, "llm_call")
builder.add_conditional_edges("llm_call", should_continue, ["tool_node", "__end__"])
builder.add_edge("tool_node", "llm_call")

memory = MemorySaver()                          # <-- YENİ: hafıza nesnesi
agent  = builder.compile(checkpointer=memory)   # <-- YENİ: graph'a bağla

# ---------------------------------------------------------------------------
# Kullanım
# ---------------------------------------------------------------------------

def chat(thread_id: str, user_message: str) -> str:
    """
    thread_id → konuşma kimliği
    Aynı thread_id ile çağırılırsa önceki mesajlar state'de zaten var,
    LangGraph bunları otomatik yükler.
    """
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke(
        {"messages": [HumanMessage(content=user_message)]},
        config=config,
    )
    return result["messages"][-1].content


if __name__ == "__main__":
    print("=" * 60)
    print("DENEY 1: Aynı thread → hafıza korunuyor")
    print("=" * 60)

    # Mesaj 1 — bir hesap yaptır
    cevap1 = chat(thread_id="t1", user_message="What is 3 multiplied by 4?")
    print(f"Kullanıcı : What is 3 multiplied by 4?")
    print(f"Ajan      : {cevap1}\n")

    # Mesaj 2 — sonucu hatırlıyor mu?
    cevap2 = chat(thread_id="t1", user_message="Now add 10 to that result.")
    print(f"Kullanıcı : Now add 10 to that result.")
    print(f"Ajan      : {cevap2}\n")

    # Mesaj 3 — hâlâ hatırlıyor mu?
    cevap3 = chat(thread_id="t1", user_message="What was the very first number I asked you to multiply?")
    print(f"Kullanıcı : What was the very first number I asked you to multiply?")
    print(f"Ajan      : {cevap3}\n")

    print("=" * 60)
    print("DENEY 2: Farklı thread → hafıza sıfırlanıyor")
    print("=" * 60)

    # Yeni thread — önceki konuşmadan haberi yok
    cevap4 = chat(thread_id="t2", user_message="What was the last calculation we did?")
    print(f"Kullanıcı : What was the last calculation we did?")
    print(f"Ajan      : {cevap4}\n")

    # ---------------------------------------------------------------------------
    # BONUS: State'e doğrudan bak (debug için çok işe yarar)
    # ---------------------------------------------------------------------------
    print("=" * 60)
    print("BONUS: t1 thread'inin state geçmişi")
    print("=" * 60)
    config_t1 = {"configurable": {"thread_id": "t1"}}
    state_snapshot = agent.get_state(config_t1)

    print(f"Toplam mesaj sayısı: {len(state_snapshot.values['messages'])}")
    for msg in state_snapshot.values["messages"]:
        role = msg.__class__.__name__
        content = str(msg.content)[:80]  # ilk 80 karakter
        print(f"  [{role}] {content}")
