from core.llm import get_llm

llm = get_llm()

def chat(user_input: str):

    messages = [
        (
            "system",
            "You are a helpful AI assistant."
        ),
        (
            "human",
            user_input
        )
    ]

    response = llm.invoke(messages)

    return response.content