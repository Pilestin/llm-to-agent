import os
import json
from datetime import datetime

CHAT_DIR = "data/chats"

os.makedirs(CHAT_DIR, exist_ok=True)


def save_chat(chat_id, messages):

    path = f"{CHAT_DIR}/{chat_id}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def load_chat(chat_id):

    path = f"{CHAT_DIR}/{chat_id}.json"

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def list_chats():

    chats = []

    for file in os.listdir(CHAT_DIR):

        if file.endswith(".json"):
            chats.append(file.replace(".json", ""))

    return sorted(chats, reverse=True)

def create_chat_id():

    return datetime.now().strftime("%Y%m%d_%H%M%S")