import time
import sounddevice as sd
import queue
import json
import speech_recognition as sr
from multiprocessing import Queue
from vosk import Model, KaldiRecognizer


def run_voice_process(event_queue: Queue):
    SAMPLE_RATE = 16000
    BLOCK_SIZE = 4000

    # English (VOSK)
    vosk_model = Model("models/en")
    recognizer = KaldiRecognizer(vosk_model, SAMPLE_RATE)

    ENGLISH_KEYWORDS = {
        "help", "emergency", "accident", "danger",
        "save", "hurt", "fall", "fire"
    }

    # Malayalam (Google ASR)
    sr_rec = sr.Recognizer()
    mic = sr.Microphone()

    MALAYALAM_KEYWORDS = {
        "സഹായം", "രക്ഷിക്കൂ", "വീണു", "അയ്യോ", "വയ്യ"
    }

    audio_q = queue.Queue()

    def audio_callback(indata, frames, time_info, status):
        audio_q.put(bytes(indata))

    def english_loop():
        while True:
            data = audio_q.get()
            if recognizer.AcceptWaveform(data):
                text = json.loads(recognizer.Result()).get("text", "").lower()
            else:
                text = json.loads(recognizer.PartialResult()).get("partial", "").lower()

            for w in ENGLISH_KEYWORDS:
                if w in text:
                    event_queue.put({
                        "type": "voice",
                        "lang": "EN",
                        "word": w,
                        "time": time.time()
                    })

    def malayalam_loop():
        with mic as source:
            sr_rec.adjust_for_ambient_noise(source)

        while True:
            try:
                with mic as source:
                    audio = sr_rec.listen(source, phrase_time_limit=4)
                text = sr_rec.recognize_google(audio, language="ml-IN")

                for w in MALAYALAM_KEYWORDS:
                    if w in text:
                        event_queue.put({
                            "type": "voice",
                            "lang": "ML",
                            "word": w,
                            "time": time.time()
                        })
            except:
                pass

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        dtype="int16",
        channels=1,
        callback=audio_callback
    ):
        import threading
        threading.Thread(target=english_loop, daemon=True).start()
        threading.Thread(target=malayalam_loop, daemon=True).start()

        while True:
            time.sleep(1)
