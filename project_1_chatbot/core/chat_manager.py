import time

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage,
    ToolMessage
)


from core.llm import get_llm


llm = get_llm()

SYSTEM_PROMPT = """
You are a helpful AI assistant.
Use tools when necessary.
"""

MAX_HISTORY = 12

def build_messages(messages):

    recent_messages = messages[-MAX_HISTORY:]

    formatted_messages = [
        SystemMessage(content=SYSTEM_PROMPT)
    ]

    for msg in recent_messages:

        if msg["role"] == "human":
            formatted_messages.append(
                HumanMessage(content=msg["content"])
            )

        elif msg["role"] == "ai":
            formatted_messages.append(
                AIMessage(content=msg["content"])
            )

    return formatted_messages


def stream_response(messages):

    formatted_messages = build_messages(messages)

    start_time = time.time()
    first_token_time = None
    full_response = ""
    total_chars = 0

    # BURASI İLK LLM CALL
    response = llm.invoke(formatted_messages)
    if response.tool_calls:
        
        formatted_messages.append(response)
        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]

            if tool_name == "get_current_time":

                from tools.datetime_tools import (
                    get_current_time
                )

                tool_result = get_current_time()
                formatted_messages.append(
                    ToolMessage(
                        content=tool_result,
                        tool_call_id=tool_call["id"]
                    )
                )
        # SECOND LLM CALL

        full_response = ""

        for chunk in llm.stream(formatted_messages):

            if chunk.content:

                full_response += chunk.content

                yield {
                    "type": "token",
                    "content": full_response
                }

    else:
        full_response = ""
    
        # BURASI LLM CALL
        for chunk in llm.stream(formatted_messages):

            content = chunk.content

            if content:

                if first_token_time is None:
                    first_token_time = time.time() - start_time
                
                full_response += content
                total_chars += len(content)

                yield {
                    "type": "token",
                    "content": full_response
                }

    end_time = time.time()

    elapsed = end_time - start_time

    # yaklaşık token hesabı
    estimated_tokens = total_chars / 4

    tokens_per_second = (
        estimated_tokens / elapsed
        if elapsed > 0
        else 0
    )

    yield {
        "type": "metrics",
        "response_time": round(elapsed, 2),
        "tokens_per_second": round(tokens_per_second, 2),
        "ttft": round(first_token_time, 2) if first_token_time else 0 
    }