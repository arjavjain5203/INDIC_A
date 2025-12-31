# modules/memory.py

import os

LOG_FILE = "logs/logs.txt"
LTM_FILE = "logs/LTM.txt"

def store_interaction(user, indica):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"You: {user}\nINDICA: {indica}\n---\n")

def get_recent_conversations(n=5):
    if not os.path.exists(LOG_FILE):
        return ""
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.read().strip().split('---\n')
        return "\n---\n".join(lines[-n:]).strip()

def clear_log():
    open(LOG_FILE, "w", encoding="utf-8").close()
