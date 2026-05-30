"""
KONU: Human-in-the-Loop (interrupt & Command)
===============================================
5_memory.py'deki agent'a her tool çağrısından ÖNCE insan onayı ekliyoruz.

TEMEL KAVRAMLAR:
  - interrupt()         : Graph'ı durdurur, dışarıya bir değer iletir
  - Command(resume=...) : Durmuş graph'ı verilen değerle devam ettirir
  - state.next          : Bekleyen node'ları gösterir; boşsa graph bitti demek
  - checkpointer        : interrupt için zorunlu — state kaydedilmeden resume mümkün değil

AKIŞ:
  START
    ↓
  llm_call ──── tool_call yok ──→ END
    │
    │ tool_call var
    ↓
  human_approval  ← interrupt() BURADA DURUYOR
    │
    ├── "yes" ──→ tool_node ──→ llm_call
    └── "no"  ──→ llm_call  (red ToolMessage ile)
"""

from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain.messages import SystemMessage, HumanMessage, AnyMessage, ToolMessage
from typing_extensions import TypedDict, Annotated
from typing import Literal
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command          # <-- YENİ

# ---------------------------------------------------------------------------
# Model & Tools (öncekiyle aynı)
# ---------------------------------------------------------------------------
model = ChatOllama(model="qwen3:8b", temperature=0)

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
# State — approved alanı eklendi
# ---------------------------------------------------------------------------
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    approved: bool

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

def human_approval_node(state: AgentState):
    """
    Tool çağrısından önce kullanıcıya sorar.

    interrupt() çağrıldığında:
      1. Graph burada durur ve state checkpoint'e kaydedilir.
      2. Dışarıya interrupt()'a verilen değer iletilir.
      3. agent.invoke(Command(resume=...), config) çağrılınca buradan devam edilir.
      4. interrupt() → Command(resume=...) içindeki değeri döner.
    """
    tool_call = state["messages"][-1].tool_calls[0]

    decision = interrupt({
        "tool_name": tool_call["name"],
        "tool_args": tool_call["args"],
        "message": (
            f"'{tool_call['name']}' tool'u "
            f"{tool_call['args']} argümanlarıyla çalıştırılmak üzere."
        ),
    })

    if decision.lower() in ("yes", "evet", "e", "y"):
        return {"approved": True}

    # Reddedildi → LLM'e "işlem reddedildi" bildirimi gönder
    return {
        "approved": False,
        "messages": [
            ToolMessage(
                content="Kullanıcı bu işlemi reddetti.",
                tool_call_id=tool_call["id"],
            )
        ],
    }

def tool_node(state: AgentState):
    result = []
    for tool_call in state["messages"][-1].tool_calls:
        t = tools_by_name[tool_call["name"]]
        observation = t.invoke(tool_call["args"])
        result.append(ToolMessage(content=str(observation), tool_call_id=tool_call["id"]))
    return {"messages": result}

# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------
def should_continue(state: AgentState) -> Literal["human_approval", "__end__"]:
    if state["messages"][-1].tool_calls:
        return "human_approval"
    return "__end__"

def after_approval(state: AgentState) -> Literal["tool_node", "llm_call"]:
    if state.get("approved"):
        return "tool_node"
    return "llm_call"

# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------
builder = StateGraph(AgentState)
builder.add_node("llm_call", llm_call)
builder.add_node("human_approval", human_approval_node)
builder.add_node("tool_node", tool_node)

builder.add_edge(START, "llm_call")
builder.add_conditional_edges("llm_call", should_continue, ["human_approval", "__end__"])
builder.add_conditional_edges("human_approval", after_approval, ["tool_node", "llm_call"])
builder.add_edge("tool_node", "llm_call")

memory = MemorySaver()                        # interrupt için checkpointer zorunlu
agent = builder.compile(checkpointer=memory)

# ---------------------------------------------------------------------------
# Yardımcı fonksiyon — interrupt/resume döngüsünü yönetir
# ---------------------------------------------------------------------------
def run_with_approval(thread_id: str, user_message: str) -> str:
    config = {"configurable": {"thread_id": thread_id}}

    # 1. İlk invoke — graph interrupt'a kadar çalışır, orada durur
    agent.invoke(
        {"messages": [HumanMessage(content=user_message)]},
        config=config,
    )

    # 2. Interrupt kuyruğu boşalana kadar döngü
    while True:
        state = agent.get_state(config)

        if not state.next:          # bekleyen node yok → graph tamamlandı
            break

        # Interrupt bilgisini al ve kullanıcıya göster
        info = state.tasks[0].interrupts[0].value
        print(f"\n  [ONAY GEREKİYOR]")
        print(f"  Tool    : {info['tool_name']}")
        print(f"  Args    : {info['tool_args']}")
        decision = input("  Onaylıyor musunuz? (yes/no): ").strip()

        # 3. Resume — graph kaldığı yerden devam eder
        agent.invoke(Command(resume=decision), config=config)

    return agent.get_state(config).values["messages"][-1].content


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("DENEY 1: Onay ver → hesaplama yapılır")
    print("=" * 55)
    r1 = run_with_approval("demo", "What is 6 multiplied by 7?")
    print(f"\nAjan: {r1}\n")

    print("=" * 55)
    print("DENEY 2: Reddet → hesaplama yapılmaz")
    print("=" * 55)
    r2 = run_with_approval("demo2", "What is 10 divided by 2?")
    print(f"\nAjan: {r2}\n")
