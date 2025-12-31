# modules/wiki.py

import wikipedia
from tts import speak

def search_wikipedia(query: str):
    """Search Wikipedia for a summary of the given query."""
    try:
        speak(f"Searching Wikipedia for {query}")
        result = wikipedia.summary(query, sentences=2)
        speak(result)
    except wikipedia.exceptions.DisambiguationError as e:
        speak("There are multiple entries for this. Please be more specific.")
    except wikipedia.exceptions.PageError:
        speak("Sorry, I could not find a page on that topic.")
    except Exception as e:
        speak("Something went wrong while searching Wikipedia.")
        print(e)
