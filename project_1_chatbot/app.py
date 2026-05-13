import streamlit as st

from core.chat_manager import stream_response

from core.storage import save_chat, load_chat, list_chats, create_chat_id

st.set_page_config(page_title="LLM To Agent", layout="wide")

st.title("LLM To Agent")

# SESSION INIT

if "chat_id" not in st.session_state:
    st.session_state.chat_id = create_chat_id()

if "messages" not in st.session_state:
    st.session_state.messages = []

# SIDEBAR

st.sidebar.title("Chats")

chat_list = list_chats()

selected_chat = st.sidebar.selectbox("Previous Chats", ["New Chat"] + chat_list)

if selected_chat == "New Chat":

    if st.sidebar.button("Create New Chat"):

        st.session_state.chat_id = create_chat_id()
        st.session_state.messages = []
        st.rerun()

else:

    if selected_chat != st.session_state.chat_id:

        st.session_state.chat_id = selected_chat
        st.session_state.messages = load_chat(selected_chat)

# DISPLAY OLD MESSAGES

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# USER INPUT

prompt = st.chat_input("Type your message...")

if prompt:

    # USER MESSAGE

    st.session_state.messages.append({"role": "human", "content": prompt})

    with st.chat_message("human"):
        st.markdown(prompt)

    # AI RESPONSE

    with st.chat_message("ai"):

        response_placeholder = st.empty()

        metrics_placeholder = st.empty()

        full_response = ""

        for event in stream_response(st.session_state.messages):

            if event["type"] == "token":

                full_response = event["content"]

                response_placeholder.markdown(full_response)

            elif event["type"] == "metrics":

                metrics_placeholder.caption(f"""
Response Time: {event['response_time']} sec | 
Tokens/sec: {event['tokens_per_second']} |
TTFT: {event['ttft']} sec 
""")

    # SAVE AI MESSAGE

    st.session_state.messages.append({"role": "ai", "content": full_response})

    # SAVE CHAT

    save_chat(st.session_state.chat_id, st.session_state.messages)
