

from langchain.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain.tools import tool
from langchain_ollama import ChatOllama


DISTANCE_MATRIX = [
    [0, 10, 15, 20],
    [10, 0, 35, 25],
    [15, 35, 0, 30],
    [20, 25, 30, 0]
]
POINTS = {
    'A': 0,
    'B': 1,
    'C': 2,
    'D': 3
}

# Bir rota sırası verildiğinde bunun distance'ını hesaplayan bir fonksiyon yazalım.
def calculate_distance(route: list[str]) -> int:
    """ Verilen bir rota sırasının distance'ını hesaplar.
    Örneğin: ['C', 'B', 'D', 'A'] rotası için:
    C -> B = 35
    B -> D = 25
    D -> A = 30
    Toplam distance = 35 + 25 + 30 = 90
    
    Args:
        route: Rota sırası, örneğin ['C', 'B', 'D', 'A']
    Returns:
        Rota sırasının distance'ı, örneğin 90
    """
    
    total_distance = 0
    for i in range(len(route) - 1):
        # rota içerisinden sırayla iki nokta alalım
        #  örneğin: C -> B, B -> D, D -> A
        #  bu noktaların id'lerini alalım
        from_node_id = route[i]
        to_node_id = route[i + 1]
        # id'si bilinen noktaların distance matrix'de nerede olduğunu bulmak için:
        #  POINTS dict içinden id'leri index'e çevirelim
        from_node_index = POINTS[from_node_id]
        to_node_index = POINTS[to_node_id]
        # aradaki mesafeyi distance matrix'den alalım ve total_distance'a ekleyelim
        total_distance += DISTANCE_MATRIX[from_node_index][to_node_index]
    return total_distance


def normalize_route(route: list[str]) -> list[str]:
    """Rota elemanlarını normalize eder ve geçerlilik kontrolü yapar."""
    normalized = [node.strip().upper() for node in route]
    invalid_nodes = [node for node in normalized if node not in POINTS]
    if invalid_nodes:
        raise ValueError(f"Geçersiz nokta(lar): {invalid_nodes}. Sadece {list(POINTS.keys())} kullanılabilir.")
    return normalized


@tool
def objective(route: list[str]) -> int:
    """Verilen rota için objective (toplam mesafe) değerini hesaplar.

    Args:
        route: Rota sırası. Ornek: ['A', 'C', 'B', 'D']
    """
    clean_route = normalize_route(route)
    return calculate_distance(clean_route)


model = ChatOllama(
    model="qwen2.5:3b",
    temperature=0,
)
model_with_tools = model.bind_tools([objective])


def run_route_chat(user_prompt: str) -> str:
    """Kullanıcı isteğini alır, objective tool'unu kullanarak sonucu döner."""
    messages = [
        SystemMessage(
            content=(
                "Sen bir rota optimizer asistanısın. Kullanıcının verdiği rota sırası için "
                "objective fonksiyonunu mutlaka tool call ile çalıştır. "
                "Yanıtında rota listesini ve objective/toplam mesafeyi net biçimde yaz. "
                "Noktalar: A, B, C, D."
            )
        ),
        HumanMessage(content=user_prompt),
    ]

    for _ in range(3):
        ai_message = model_with_tools.invoke(messages)
        messages.append(ai_message)

        if isinstance(ai_message, AIMessage) and ai_message.tool_calls:
            for tool_call in ai_message.tool_calls:
                if tool_call["name"] != "objective":
                    continue
                try:
                    observation = objective.invoke(tool_call["args"])
                except Exception as exc:
                    observation = f"HATA: {exc}"

                messages.append(
                    ToolMessage(content=str(observation), tool_call_id=tool_call["id"])
                )
            continue

        return str(ai_message.content)

    return "Tool call tamamlanamadi. Lutfen rotayi ornek formatta ver: ['A', 'C', 'B', 'D']"


if __name__ == "__main__":
    print("Rota optimizer chati basladi. Cikmak icin 'q' yaz.")
    while True:
        user_input = input("Sen: ").strip()
        if user_input.lower() in {"q", "quit", "exit"}:
            print("Cikis yapildi.")
            break

        answer = run_route_chat(user_input)
        print(f"Ajan: {answer}")