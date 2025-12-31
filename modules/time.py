# modules/time_module.py

from datetime import datetime
from tts import speak

def get_time():
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")  # 12-hour format with AM/PM
    speak(f"The current time is {current_time}")
