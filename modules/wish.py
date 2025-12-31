# modules/wish.py

from tts import speak
import datetime

def wish_me():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    speak(f"{greeting} Sir. How may I assist you today?")

