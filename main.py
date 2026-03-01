import time
from multiprocessing import Process, Queue, Value

from decision_engine import EmergencyDecisionEngine
from fall_process import run_fall_process
from voice_process import run_voice_process



if __name__ == "__main__":
    print("\n🚀 MULTIPROCESS EMERGENCY SYSTEM STARTED\n")

    event_queue = Queue()
    # Shared flag for emergency state (False = 0, True = 1)
    emergency_flag = Value('b', False)
    
    engine = EmergencyDecisionEngine(emergency_flag)

    fall_p = Process(target=run_fall_process, args=(event_queue, 0, emergency_flag))
    voice_en_p = Process(target=run_voice_process, args=(event_queue,))

    fall_p.start()
    voice_en_p.start()

    try:
        while True:
            event = event_queue.get()

            if event["type"] == "fall_state":
                print(f"📡 Fall event received: {event['state']}")
                engine.update_fall_state(event["state"], event["time"])

            elif event["type"] == "voice":
                engine.register_voice_keyword(event["word"], event["time"])

    except KeyboardInterrupt:
        print("\n🛑 Shutting down system")
        fall_p.terminate()
        voice_en_p.terminate()

