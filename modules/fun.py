# modules/fun.py

from tts import speak
import pyjokes

def tell_joke():
    """Tell a random joke."""
    joke = pyjokes.get_joke()
    speak(joke)

def sing_rap():
    """Performs a basic rap."""
    rap = (
        "Yo yo yo, I'm INDICA in the flow, fast like light, always on the go.\n"
        "Ask me a question, I'm ready to show, knowledge power, let’s roll the show."
    )
    speak(rap)
