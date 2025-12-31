from tts import speak
import webbrowser

def play_music(query: str = "lofi music"):
    """Play music using YouTube search."""
    if not query.strip():
        query = "lofi music"
    speak(f"Playing {query} on YouTube.")
    search_url = f"https://www.youtube.com/results?search_query={'+'.join(query.split())}"
    webbrowser.open(search_url)
