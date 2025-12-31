# modules/location.py

import webbrowser
from tts import speak

def locate_place(place: str):
    """Opens Google Maps with the given location."""
    if not place:
        speak("Please specify the location.")
        return
    speak(f"Showing the location of {place}")
    webbrowser.open(f"https://www.google.com/maps/place/{place.replace(' ', '+')}")
