import time
import cv2
from multiprocessing import Queue
from fall import SimpleHighAccuracyFallDetector


def run_fall_process(event_queue: Queue, cam_index=1, emergency_flag=None):
    detector = SimpleHighAccuracyFallDetector()

    def fall_state_callback(state, timestamp):
        event_queue.put({
            "type": "fall_state",
            "state": state,
            "time": timestamp
        })

    detector.on_state_change = fall_state_callback

    # ✅ ROBUST CAMERA INITIALIZATION
    cap = None
    # Try different backends in order of preference for Windows
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, None] 
    
    found = False
    for backend in backends:
        if found: break
        for idx in [cam_index, 0, 1, 2]:
            if backend is not None:
                cap = cv2.VideoCapture(idx, backend)
            else:
                cap = cv2.VideoCapture(idx)
            
            if cap.isOpened():
                # Test if we can actually read a frame
                ret, _ = cap.read()
                if ret:
                    print(f"📷 Camera opened successfully (Index: {idx}, Backend: {backend})")
                    found = True
                    break
                else:
                    cap.release()
    
    if not found or cap is None:
        print("❌ CRITICAL: Could not start any camera!")
        event_queue.put({"type": "error", "source": "camera"})
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # ✅ NEW: confirm camera + fall pipeline is alive
    event_queue.put({
        "type": "fall_state",
        "state": "CAMERA_ACTIVE",
        "time": time.time()
    })

    print("📷 Camera opened, fall detection running")

    last_heartbeat_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.05)
            continue

        fall_conf, stand_conf, keypoints = detector.process_frame_fast(frame)
        
        is_emergency = False
        if emergency_flag:
            is_emergency = bool(emergency_flag.value)
            
        detector.draw_results(frame, fall_conf, stand_conf, keypoints, emergency_active=is_emergency)

        # ✅ HEARTBEAT: Force update every 0.5s if fall is active
        # This ensures the decision engine checks the time duration
        now = time.time()
        if detector.state == "FALL_DETECTED" and (now - last_heartbeat_time > 0.5):
            event_queue.put({
                "type": "fall_state",
                "state": "FALL_DETECTED",
                "time": now
            })
            last_heartbeat_time = now

        cv2.imshow("Fall Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
