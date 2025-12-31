# modules/clock.py

import time
import datetime
import threading
from tts import speak
from datetime import datetime
from tts import speak

def get_date():
    """Speaks the current date."""
    today = datetime.now()
    date_str = today.strftime("%A, %B %d, %Y")
    speak(f"Today is {date_str}.")

def start_stopwatch():
    speak("Stopwatch started. Say stop stopwatch to stop.")
    global stopwatch_start
    stopwatch_start = time.time()

def stop_stopwatch():
    if stopwatch_start:
        elapsed = time.time() - stopwatch_start
        speak(f"Stopwatch stopped. Elapsed time: {elapsed:.2f} seconds.")
    else:
        speak("Stopwatch was never started.")

def set_timer(seconds: int):
    def countdown():
        speak(f"Timer set for {seconds} seconds.")
        time.sleep(seconds)
        speak("Time's up!")

    threading.Thread(target=countdown, daemon=True).start()

def set_alarm(alarm_time: str):
    def alarm_loop():
        speak(f"Alarm set for {alarm_time}")
        while True:
            now = datetime.datetime.now().strftime("%H:%M")
            if now == alarm_time:
                speak("Alarm ringing! Wake up!")
                break
            time.sleep(10)

    threading.Thread(target=alarm_loop, daemon=True).start()
