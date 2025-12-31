# modules/weather.py

import requests
from tts import speak
from config import DEFAULT_CITY, WEATHERSTACK_API_KEY

def get_weather(city=None):
    """
    Fetches weather info for a given city or default city.
    """
    city = city or DEFAULT_CITY
    base_url = f"http://api.weatherstack.com/current?access_key={WEATHERSTACK_API_KEY}&query={city}"

    try:
        response = requests.get(base_url)
        data = response.json()

        if 'current' not in data:
            speak(f"Sorry, I couldn't find weather data for {city}.")
            return

        temperature = data['current']['temperature']
        description = data['current']['weather_descriptions'][0]
        speak(f"It is currently {temperature} degrees Celsius in {city} with {description}.")

    except Exception as e:
        speak(f"Failed to get weather: {e}")
