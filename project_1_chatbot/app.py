import streamlit as st

from core.chat_manager import generate_response
from core.storage import (
    save_chat,
    load_chat,
    list_chats,
    create_chat_id
)

st.set_page_config(page_title="LLM To Agent")

st.title("LLM To Agent")

# SESSION INIT

if "chat_id" not in st.session_state:
    st.session_state.chat_id = create_chat_id()

if "messages" not in st.session_state:
    st.session_state.messages = []

# SIDEBAR

st.sidebar.title("Previous Chats")

chat_list = list_chats()

selected_chat = st.sidebar.selectbox(
    "Select Chat",
    ["New Chat"] + chat_list
)

if selected_chat != "New Chat":

    if selected_chat != st.session_state.chat_id:

        st.session_state.chat_id = selected_chat
        st.session_state.messages = load_chat(selected_chat)

# DISPLAY CHAT

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# USER INPUT

prompt = st.chat_input("Type your message...")

if prompt:

    # Add user message

    st.session_state.messages.append({
        "role": "human",
        "content": prompt
    })

    with st.chat_message("human"):
        st.markdown(prompt)

    # Generate AI response

    response = generate_response(
        st.session_state.messages
    )

    st.session_state.messages.append({
        "role": "ai",
        "content": response
    })

    with st.chat_message("ai"):
        st.markdown(response)

    # Save chat

    save_chat(
        st.session_state.chat_id,
        st.session_state.messages
    )