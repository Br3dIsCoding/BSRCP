import pygame
import speech_recognition as sr
import whisper
import os
import sys
import time
import tempfile
import re
import threading


def _base_dir():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "no_cursing")
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = _base_dir()

pygame.mixer.init()

# ===== STATE =====
running = False
model = None

transcript_callback = None

def set_transcript_callback(func):
    global transcript_callback
    transcript_callback = func

# ===== AUDIO =====
def play_sound_wait(filename):
    path = os.path.join(BASE_DIR, filename)
    sound = pygame.mixer.Sound(path)
    channel = sound.play()
    while channel.get_busy():
        pygame.time.wait(50)

# ===== SWEAR LIST =====
swear_words = [
    "fuck","fucking","fucked","shit","shitty","bitch","bastard","ass",
    "asshole","damn","goddamn","hell","crap","piss","pissed","dick",
    "douche","slut","whore","bullshit","wtf","motherfucker",
    "son of a bitch","cunt","jesus","christ","god","jesus christ almighty"
]

# ===== SWEAR DETECTION =====
def count_swears(message, words):
    text = message.lower()
    sorted_words = sorted(words, key=len, reverse=True)
    taken = [False] * len(text)
    matches = []

    for word in sorted_words:
        pattern = re.compile(rf"(?<!\w){re.escape(word)}(?!\w)")
        for m in pattern.finditer(text):
            start, end = m.span()
            if any(taken[i] for i in range(start, end)):
                continue
            for i in range(start, end):
                taken[i] = True
            matches.append(word)

    return len(matches), matches

# ===== MAIN LOOP =====
def listen_loop(mic_index):
    global running, model

    r = sr.Recognizer()
    r.pause_threshold = 1.1
    r.non_speaking_duration = 0.6

    with sr.Microphone(device_index=mic_index) as source:
        print("Calibrating mic...")
        r.adjust_for_ambient_noise(source, duration=1)
        print("Listening started.")

        while running:
            try:
                audio = r.listen(source, timeout=5)
                wav_data = audio.get_wav_data()

                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(wav_data)
                    tmp_path = tmp.name

                try:
                    result = model.transcribe(tmp_path)
                    text = result.get("text", "").strip()
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

                if not text:
                    continue

                print("You said:", text)
                if transcript_callback:
                    transcript_callback(text)

                swear_count, found_words = count_swears(text, swear_words)

                if swear_count > 0:
                    print(f"Swears detected: {swear_count} -> {found_words}")

                    for i in range(swear_count):
                        if found_words[i] == "jesus christ almighty":
                            play_sound_wait("jesus_christ.mp3")

                        play_sound_wait("BOOM.mp3")


            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print("Error:", e)

    print("Stopped listening")

# ===== START / STOP =====
def start(mic_index):
    global running, model

    if running:
        return

    print("Starting NoSwear system...")
    running = True

    if model is None:
        print("Loading Whisper model...")
        model = whisper.load_model("base")

    play_sound_wait("swearing_disabled.mp3")

    threading.Thread(target=listen_loop, args=(mic_index,), daemon=True).start()


def stop():
    global running
    running = False
    print("Stopping NoSwear system...")
    play_sound_wait("swearing_enabled.mp3")