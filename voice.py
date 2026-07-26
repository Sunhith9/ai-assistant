"""
voice.py
Text-to-speech agent - speaks out the assistant's response.
Uses pyttsx3 for offline text-to-speech synthesis.
"""

import pyttsx3

def speak(text: str) -> None:
    """Speak the given text using text-to-speech."""
    try:
        # Initialize the pyttsx3 engine
        engine = pyttsx3.init()
        
        # Adjust settings (optional, e.g., speed rate)
        # Default rate is usually 200, setting it to 175 makes it slightly more natural
        engine.setProperty('rate', 175)
        
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[Voice agent error: {e}]")
