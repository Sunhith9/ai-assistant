"""
listen.py
Speech-to-text agent - continuously listens to your microphone and stops
automatically when you pause speaking (silence detection), instead of a
fixed time window. Uses Google's free web speech recognition.
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import os
import speech_recognition as sr

_recognizer = sr.Recognizer()

SAMPLE_RATE = 16000
MIC_DEVICE_INDEX = 5  # change to 113 if this mic doesn't pick up sound
sd.default.device = (MIC_DEVICE_INDEX, None)

CHUNK_DURATION = 0.5          # seconds per audio chunk checked
SILENCE_THRESHOLD = 0.02      # volume level below this counts as silence
SILENCE_LIMIT = 1.2           # seconds of silence after speech before stopping
MAX_DURATION = 30             # hard safety cap in seconds


def listen() -> str:
    """Continuously record until the user pauses speaking, then return
    the recognized text. Returns an empty string if nothing was understood.
    """
    print("[Listening... speak whenever you're ready]")

    chunk_samples = int(CHUNK_DURATION * SAMPLE_RATE)
    silence_chunks_needed = int(SILENCE_LIMIT / CHUNK_DURATION)
    max_chunks = int(MAX_DURATION / CHUNK_DURATION)

    frames = []
    silence_count = 0
    started_talking = False

    try:
        stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32")
        stream.start()

        for _ in range(max_chunks):
            chunk, _ = stream.read(chunk_samples)
            volume = float(np.abs(chunk).mean())
            frames.append(chunk)

            if volume > SILENCE_THRESHOLD:
                started_talking = True
                silence_count = 0
            elif started_talking:
                silence_count += 1
                if silence_count >= silence_chunks_needed:
                    break

        stream.stop()
        stream.close()
    except Exception as e:
        print(f"[Microphone error: {e}]")
        return ""

    if not started_talking:
        return ""

    recording = np.concatenate(frames, axis=0)

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        sf.write(tmp_path, recording, SAMPLE_RATE)

        with sr.AudioFile(tmp_path) as source:
            audio = _recognizer.record(source)

        text = _recognizer.recognize_google(audio)
        print(f"[Heard: {text}]")
        return text
    except sr.UnknownValueError:
        print("[Could not understand audio]")
        return ""
    except sr.RequestError as e:
        print(f"[Speech recognition error: {e}]")
        return ""
    except Exception as e:
        print(f"[Listen agent error: {e}]")
        return ""
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)