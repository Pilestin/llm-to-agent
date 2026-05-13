from core.llm import get_llm

llm = get_llm()

SYSTEM_PROMPT = """
You are a helpful AI assistant.
"""

def generate_response(messages):

    formatted_messages = [
        ("system", SYSTEM_PROMPT)
    ]

    for msg in messages:
        formatted_messages.append(
            (msg["role"], msg["content"])
        )

    response = llm.invoke(formatted_messages)

    return response.content