from modules.wish import wish_me
from ai_engine.gemini_engine import query_gemini
from dispatcher import dispatch
from tts import speak
from listener import take_command
from modules.memory import store_interaction, get_recent_conversations

def main():
    wish_me()

    while True:
        user_input = take_command()

        if not user_input or not user_input.strip():
            continue

        if user_input.lower() in ["exit", "quit", "stop"]:
            speak("Goodbye, Sir.")
            break

        result = query_gemini(user_input)

        if not result or not isinstance(result, dict):
            speak("Sorry, I couldn't process that.")
            continue

        # Speak Gemini's reply always
        response = result.get("response")
        if response:
            speak(response)
            store_interaction(user_input, response)

        # Handle actions if any
        actions = result.get("actions", [])
        if actions:
            dispatch(actions, result)

        # No action, just chat
        elif not actions:
            # No need to say "I don't know what to do"
            # This allows LLM-style conversation
            continue

if __name__ == "__main__":
    main()
