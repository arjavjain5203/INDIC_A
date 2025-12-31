# ai_engine/gemini_engine.py

from modules.LTM import LongTermMemory
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL
import json
import re

def extract_json(text):
    cleaned = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()

    try:
        parsed = json.loads(cleaned)
        return {
            "response": parsed.get("response", ""),
            "actions": parsed.get("actions", []),
            "locations": parsed.get("locations", []),
            "query": parsed.get("query", ""),
            "email_subject": parsed.get("email_subject", ""),
            "email_body": parsed.get("email_body", ""),
            "to_email": parsed.get("to_email", "")
        }
    except json.JSONDecodeError:
        return {
            "response": cleaned,
            "actions": [],
            "locations": [],
            "query": "",
            "email_subject": "",
            "email_body": "",
            "to_email": ""
        }


def get_recent_conversations(filepath="logs/logs.txt", max_pairs=5):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Split the content by the '---' separator to get individual conversation blocks
        conversation_blocks = [block.strip() for block in content.split("---") if block.strip()]

        conversations = []
        # Iterate over the conversation blocks in reverse order to get the most recent ones
        for block in reversed(conversation_blocks):
            user_line = ""
            ai_line = ""
            # Split the block into lines and find the user and AI parts
            for line in block.split('\n'):
                line_stripped = line.strip()
                if line_stripped.startswith("You:"):
                    user_line = line_stripped.replace("You:", "").strip()
                elif line_stripped.startswith("INDICA:"):
                    ai_line = line_stripped.replace("INDICA:", "").strip()

            # If both user and AI parts are found, add to conversations
            if user_line and ai_line:
                conversations.insert(0, f"User: {user_line} | INDICA: {ai_line}")
                if len(conversations) >= max_pairs:
                    break
        
        return "\n".join(conversations) if conversations else "No recent memory."

    except FileNotFoundError:
        return "No recent memory."
    except Exception as e:
        # Catch any other potential errors during file processing
        return f"An error occurred: {e}"

def query_gemini(query):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)

        # 🔁 Short-term memory from logs
        conversation_history = get_recent_conversations("logs/logs.txt")

        # 🧠 Long-term memory from LTM module
        ltm = LongTermMemory()
        ltm_facts = ltm.search(query, top_k=5)
        ltm_context = "\n".join([f"{fact['key']}: {fact['value']}" for fact in ltm_facts])

        # 🤖 Build Gemini Prompt
        prompt = f"""
You are INDICA — a charming and context-aware, voice AI assistant made by Abhey Tiwari. Your memory works in two parts:

1. 🔁 Short-Term Memory (Recent Conversations):
{conversation_history}

2. 🧠 Long-Term Memory (Past Data, Projects, People, Preferences): whenevr I ask about myself or anything personal or freinds or family check your long term memory, Do not hold back any information:
{ltm_context}

You must generate context-aware JSON replies that align with both memories.

You always answer clearly, in JSON format only — no markdown or code block wrappers.

Your task is to respond to the user and detect intent.

📧 If a user asks you to send an email, you MUST include these fields:
- "email_subject"
- "email_body"
- "to_email"

🧠 If the user wants you to do deep research on a topic, use:
{{
  "response": "Sure, let me research that for you.",
  "actions": ["perform_research"],
  "locations": [],
  "query": "Impact of forest fires in India"
}}

Allowed Actions:
["get_time", "get_date", "get_weather", "play_music", "tell_joke",
"fun_response", "search_web", "wiki_search", "search_wikihow",
"get_location", "open_app", "open_calculator", "open_google", "open_youtube",
"send_email", "start_stopwatch", "stop_stopwatch", "set_timer", "set_alarm",
"wish_user", "system_op", "lockdown", "self_destruct", "perform_research"]

User said:
{query}
"""

        # 🔥 Get Gemini's response
        response = model.generate_content(prompt)
        return extract_json(response.text.strip())

    except Exception as e:
        return {
            "response": f"Gemini error: {e}",
            "actions": [],
            "locations": [],
            "query": ""
        }