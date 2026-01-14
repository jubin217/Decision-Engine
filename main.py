import time
from multiprocessing import Process, Queue
from decision_engine import EmergencyDecisionEngine
from fall_process import run_fall_process
from voice_process import run_voice_process


if __name__ == "__main__":
    print("\n🚀 MULTIPROCESS EMERGENCY SYSTEM STARTED\n")

    event_queue = Queue()
    engine = EmergencyDecisionEngine()

    fall_p = Process(target=run_fall_process, args=(event_queue, 1))
    voice_p = Process(target=run_voice_process, args=(event_queue,))

    fall_p.start()
    voice_p.start()

    try:
        while True:
            event = event_queue.get()

            if event["type"] == "fall_state":
                engine.update_fall_state(event["state"], event["time"])

            elif event["type"] == "voice":
                engine.register_voice_keyword(event["word"], event["time"])

    except KeyboardInterrupt:
        print("\n🛑 Shutting down system")
        fall_p.terminate()
        voice_p.terminate()
