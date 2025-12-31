# modules/sytem.py

import os
import subprocess
from tts import speak

def perform_system_op(command: str):
    """Performs basic system operations like shutdown, restart."""
    command = command.lower()
    
    if "shutdown" in command:
        speak("Shutting down the system.")
        os.system("shutdown /s /t 1")
    
    elif "restart" in command:
        speak("Restarting the system.")
        os.system("shutdown /r /t 1")
    
    elif "lock" in command:
        speak("Locking the system.")
        subprocess.call("rundll32.exe user32.dll,LockWorkStation")
    
    else:
        speak("Sorry, I didn't understand the system command.")
