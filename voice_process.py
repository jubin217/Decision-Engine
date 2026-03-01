import time
import queue
import json
import sounddevice as sd
import speech_recognition as sr
from multiprocessing import Queue
from vosk import Model, KaldiRecognizer

print("🎤 Unified Voice Process Started")

def run_voice_process(event_queue: Queue):
    SAMPLE_RATE = 16000
    BLOCK_SIZE = 4000

    # ---------- AUDIO QUEUE ----------
    audio_q = queue.Queue()

    def audio_callback(indata, frames, time_info, status):
        audio_q.put(bytes(indata))

    # ---------- ENGLISH (VOSK) ----------
    vosk_model = Model("models/en")
    vosk_rec = KaldiRecognizer(vosk_model, SAMPLE_RATE)

    ENGLISH_KEYWORDS = {
        "help", "emergency", "accident", "danger",
        "save", "hurt", "fall", "fire"
    }

    # ---------- MALAYALAM (GOOGLE ASR) ----------
    sr_rec = sr.Recognizer()

    MALAYALAM_KEYWORDS = {
        "സഹായം", "രക്ഷിക്കൂ", "വീണു",
        "അയ്യോ", "വയ്യ"
    }

    last_ml_time = 0

    print("🎤 Mic acquired (single owner)")

    while True:
        try:
            with sd.RawInputStream(
                samplerate=SAMPLE_RATE,
                blocksize=BLOCK_SIZE,
                dtype="int16",
                channels=1,
                callback=audio_callback
            ):
                print("🎤 Stream active")
                while True:
                    data = audio_q.get()

                    # ---------- ENGLISH (FAST) ----------
                    if vosk_rec.AcceptWaveform(data):
                        text = json.loads(vosk_rec.Result()).get("text", "").lower()
                    else:
                        text = json.loads(vosk_rec.PartialResult()).get("partial", "").lower()

                    for w in ENGLISH_KEYWORDS:
                        if w in text:
                            event_queue.put({
                                "type": "voice",
                                "lang": "EN",
                                "word": w,
                                "time": time.time()
                            })
                            print(f"🔊 EN detected: {w}")

                    # ---------- MALAYALAM (SLOW, PERIODIC) ----------
                    now = time.time()
                    if now - last_ml_time > 2:   # throttle Google ASR
                        last_ml_time = now
                        try:
                            audio = sr.AudioData(data, SAMPLE_RATE, 2)
                            ml_text = sr_rec.recognize_google(audio, language="ml-IN")

                            for w in MALAYALAM_KEYWORDS:
                                if w in ml_text:
                                    event_queue.put({
                                        "type": "voice",
                                        "lang": "ML",
                                        "word": w,
                                        "time": now
                                    })
                                    print(f"🔊 ML detected: {w}")

                        except sr.UnknownValueError:
                            pass
                        except sr.RequestError:
                            print("⚠️ Google Speech API unavailable")
                        except Exception as e:
                            print(f"⚠️ MLA processing error: {e}")

        except Exception as e:
            print(f"🔴 Stream error: {e}. Restarting in 1s...")
            time.sleep(1)
