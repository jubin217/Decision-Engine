import time
import cv2
from multiprocessing import Queue
from fall import SimpleHighAccuracyFallDetector


def run_fall_process(event_queue: Queue, cam_index=1):
    detector = SimpleHighAccuracyFallDetector()

    def fall_state_callback(state, timestamp):
        event_queue.put({
            "type": "fall_state",
            "state": state,
            "time": timestamp
        })

    detector.on_state_change = fall_state_callback

    cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        event_queue.put({"type": "error", "source": "camera"})
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.05)
            continue

        detector.process_frame_fast(frame)
        detector.draw_results(frame)

        cv2.imshow("Fall Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
