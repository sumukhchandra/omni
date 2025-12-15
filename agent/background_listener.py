#!/usr/bin/env python3
"""
Cross-platform background listener using Vosk + sounddevice.
Drop into background_listener.py in project root.

Requires:
- vosk
- sounddevice
- pyttsx3
- requests
"""
import os, sys, json, time, re
from difflib import SequenceMatcher
try:
    import sounddevice as sd
    from vosk import Model, KaldiRecognizer
    import requests
    import pyttsx3
except Exception as e:
    print("Missing dependencies. Run: pip install vosk sounddevice requests pyttsx3")
    print("Exception:", e)
    sys.exit(1)

ROOT = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(ROOT, "models", "vosk-small-en-us-0.15")
SERVER_URL = "http://127.0.0.1:5005/command"
SAMPLE_RATE = 16000

# Tunables
LISTEN_SECS = 5
CONFIRM_SECS = 3
AUTO_EXEC_CONF = 0.75
FUZZY_MAP_THRESHOLD = 0.6
WAKEWORD = "bro"

DRY_RUN = os.environ.get("DRY_RUN","0") == "1"
DEBUG = True

# simple mapping (extend)
COMMAND_WHITELIST = {
    "command plus tab": ["command plus tab", "press command tab", "cmd tab", "command plus tab please"],
    "open spotify": ["open spotify", "open the spotify", "launch spotify"],
    "play hanuman song in spotify": ["play hanuman song", "play hanuman", "play hanuman song in spotify"],
    "open whatsapp": ["open whatsapp", "open whatsapp app", "launch whatsapp"],
    "call vinnu video call": ["call vinnu video call", "video call vinnu", "call vinnu"],
    "inspect": ["inspect", "take screenshot", "inspect screen"],
    "press add button": ["press add button", "press plus", "press + button"],
}

# common mishears
NORMALIZATION_REPLACEMENTS = [
    (r"\bcommon\b", "command"),
    (r"\bor been\b", "open"),
    (r"\bbravo\b", "bro"),
    (r"\bcomon\b", "command"),
]

import queue
q = queue.Queue()

def normalize_asr_text(text: str) -> str:
    t = text.lower().strip()
    for patt, repl in NORMALIZATION_REPLACEMENTS:
        t = re.sub(patt, repl, t)
    t = re.sub(r"\s+", " ", t)
    return t

def best_whitelist_match(text: str):
    text = text.lower().strip()
    best = (None, 0.0, None)
    for norm, syns in COMMAND_WHITELIST.items():
        for s in syns:
            score = SequenceMatcher(None, text, s).ratio()
            if score > best[1]:
                best = (norm, score, s)
    return best

def speak(text: str):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        if DEBUG: print("TTS error:", e)

def send_to_server(text: str):
    payload = {"text": text}
    if DRY_RUN:
        if DEBUG: print("[DRY_RUN] send:", payload)
        return {"ok": True, "dry": True}
    try:
        r = requests.post(SERVER_URL, json=payload, timeout=8)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

# audio capture
def audio_callback(indata, frames, time_info, status):
    q.put(bytes(indata))

def run_listener():
    if not os.path.isdir(MODEL_PATH):
        print("ERROR: Vosk model not found at:", MODEL_PATH)
        sys.exit(1)

    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)

    print("Starting audio. Say wakeword 'bro'.")
    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype='int16',
                           channels=1, callback=audio_callback):
        wake_waiting = False
        wake_expiry = 0
        while True:
            try:
                data = q.get(timeout=0.5)
            except Exception:
                if wake_waiting and time.time() > wake_expiry:
                    wake_waiting = False
                continue

            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                text = res.get("text", "").strip()
                if not text:
                    continue
                if WAKEWORD in text.split():
                    after = text.split(WAKEWORD,1)[1].strip()
                    if after:
                        # "bro open spotify" one utterance
                        cand = normalize_asr_text(after)
                        mapped, score, syn = best_whitelist_match(cand)
                        if mapped and score >= FUZZY_MAP_THRESHOLD:
                            print("Mapping:", mapped, "score", score)
                            resp = send_to_server(mapped)
                            print("SERVER RESP:", resp)
                        else:
                            speak("Please repeat the command.")
                        continue
                    # just wakeword -> start window
                    wake_waiting = True
                    wake_expiry = time.time() + LISTEN_SECS
                    print("Wakeword detected, listening for", LISTEN_SECS, "s")
                    continue

                # if we are in wake window, treat this as candidate command
                if wake_waiting:
                    wake_waiting = False
                    cand = normalize_asr_text(text)
                    mapped, score, syn = best_whitelist_match(cand)
                    print("Candidate:", cand, "mapped:", mapped, "score", score)
                    if mapped and score >= FUZZY_MAP_THRESHOLD:
                        # send or confirm depending on confidence (we don't have word-level conf easily here)
                        resp = send_to_server(mapped)
                        print("SERVER RESP:", resp)
                    else:
                        speak("I did not understand. Please repeat.")
            else:
                # partial result
                partial = json.loads(rec.PartialResult()).get("partial","").strip()
                if WAKEWORD in partial.split() and not wake_waiting:
                    wake_waiting = True
                    wake_expiry = time.time() + LISTEN_SECS
                    print("[PARTIAL] Wakeword seen -> starting wake window")

if __name__ == "__main__":
    run_listener()
