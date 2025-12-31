from tts import speak
import webbrowser

def search_web(query: str = ""):
    """Performs a web search using Google."""
    if not query or not isinstance(query, str) or not query.strip():
        speak("What should I search for?")
        return
    speak(f"Searching for {query} on Google.")
    search_url = f"https://www.google.com/search?q={'+'.join(query.split())}"
    webbrowser.open(search_url)

