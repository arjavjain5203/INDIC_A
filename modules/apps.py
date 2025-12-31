import os
import json
import subprocess
import re
from difflib import get_close_matches
# Assuming 'tts' module and 'speak' function are correctly implemented and accessible
from tts import speak

# Dynamically locate apps.json inside the same folder
APP_JSON_PATH = os.path.join(os.path.dirname(__file__), "apps.json")

# Load app path mappings
try:
    with open(APP_JSON_PATH, "r") as f:
        APP_PATHS = json.load(f)
except FileNotFoundError:
    speak("App mapping file not found. Please ensure apps.json is in the same directory.")
    APP_PATHS = {}
except json.JSONDecodeError as e:
    speak(f"Error reading apps.json: Invalid JSON format. {str(e)}")
    APP_PATHS = {}
except Exception as e: # Catch any other potential file reading errors
    speak(f"An unexpected error occurred while loading apps.json: {str(e)}")
    APP_PATHS = {}


def clean_input(query: str) -> str:
    query = query.lower()
    # Expanded common filler words
    query = re.sub(r"\b(open|launch|start|run|the|app|application|please|a|up|can you|could you)\b", "", query)
    return query.strip()

def open_application(query: str):
    raw_input = clean_input(query)

    if not raw_input:
        speak("Can you please specify which application you would like me to open?")
        return

    print(f"[DEBUG] Parsed app name for lookup: '{raw_input}'")

    matched = get_close_matches(raw_input, APP_PATHS.keys(), n=1, cutoff=0.6)

    if not matched:
        speak(f"Sorry, I don't recognize the application '{raw_input}'. Please make sure it's added to my list or try a different phrasing.")
        return

    app_name = matched[0]
    path = APP_PATHS[app_name]

    speak(f"Okay, attempting to open {app_name} for you.")
    print(f"[DEBUG] Attempting to open '{app_name}' at path: '{path}'")

    try:
        if os.path.isdir(path):
            # Use os.startfile for opening folders/directories
            os.startfile(path)
            speak(f"{app_name} folder is now open.")
        elif path.lower().startswith("shell:appsfolder"):
            # Use subprocess.Popen with explorer.exe for Windows Store Apps (UWP)
            subprocess.Popen(f'explorer.exe "{path}"', shell=True)
            speak(f"{app_name} launched successfully via Windows Shell.")
        else:
            # For .exe, .bat, .lnk, or system commands (like 'notepad.exe')
            # os.startfile is generally preferred for opening, but Popen with shell=True
            # is robust for system commands not found in current directory.
            # If path points to an executable, os.startfile often works well.
            # If it's a command like "notepad.exe" in PATH, shell=True is needed with Popen.
            # Let's keep Popen with shell=True for broad compatibility here.
            subprocess.Popen(path, shell=True)
            speak(f"{app_name} launched successfully.")

    except FileNotFoundError:
        speak(f"The file or application at '{path}' was not found. Please check the path in apps.json.")
    except PermissionError:
        speak(f"Permission denied to launch {app_name}. You might need administrator privileges.")
    except Exception as e:
        # Catch other unexpected errors during launch
        speak(f"An unexpected error occurred while launching {app_name}. Error: {str(e)}")
        print(f"[ERROR] Failed to launch {app_name} ('{path}'). Error details: {e}")