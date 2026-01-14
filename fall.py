import cv2
import numpy as np
from ultralytics import YOLO
import time
from collections import deque
import warnings
warnings.filterwarnings('ignore')


class SimpleHighAccuracyFallDetector:
    def __init__(self):
        print("Loading YOLOv8 Pose Estimation for fall detection...")
        self.on_state_change = None  # callback hook

        self.pose_model = YOLO("yolov8n-pose.pt")

        self.state = "MONITORING"
        self.total_falls = 0
        self.consecutive_fall_frames = 0
        self.consecutive_stand_frames = 0
        self.fall_start_time = 0

        self.fall_confidence_threshold = 0.65
        self.required_fall_frames = 5
        self.required_stand_frames = 8

        self.fall_confidence_history = deque(maxlen=8)
        self.pose_history = deque(maxlen=10)

        print("✅ Fall detection system ready!")
        print("📊 Using proven pose-based fall detection algorithms")

    # ================= CONFIDENCE CALCS =================
    def calculate_fall_confidence(self, keypoints, frame_shape):
        if keypoints is None or len(keypoints) == 0:
            return 0.0

        confidence_scores = []
        keypoints = keypoints[0]

        if len(keypoints) >= 13:
            ls, rs = keypoints[5], keypoints[6]
            lh, rh = keypoints[11], keypoints[12]

            if all(kp[2] > 0.2 for kp in [ls, rs, lh, rh]):
                shoulder_center = (ls[:2] + rs[:2]) / 2
                hip_center = (lh[:2] + rh[:2]) / 2

                dx = hip_center[0] - shoulder_center[0]
                dy = hip_center[1] - shoulder_center[1]

                angle = np.degrees(np.arctan2(abs(dx), abs(dy))) if abs(dy) > 1e-3 else 90
                angle_conf = max(0, min(1, (angle - 30) / 60))
                confidence_scores.append(angle_conf * 0.5)

        return min(1.0, sum(confidence_scores)) if confidence_scores else 0.0

    def calculate_stand_confidence(self, keypoints):
        if keypoints is None or len(keypoints) == 0:
            return 0.0

        keypoints = keypoints[0]
        scores = []

        if len(keypoints) >= 13:
            ls, rs = keypoints[5], keypoints[6]
            lh, rh = keypoints[11], keypoints[12]

            if all(kp[2] > 0.2 for kp in [ls, rs, lh, rh]):
                shoulder_center = (ls[:2] + rs[:2]) / 2
                hip_center = (lh[:2] + rh[:2]) / 2
                dy = hip_center[1] - shoulder_center[1]
                scores.append(1.0 if dy > 0 else 0.0)

        return np.mean(scores) if scores else 0.0

    # ================= STATE MACHINE =================
    def update_state_machine(self, fall_conf, stand_conf):
        now = time.time()

        if self.state == "MONITORING":
            if fall_conf > self.fall_confidence_threshold:
                self.consecutive_fall_frames += 1
                self.fall_confidence_history.append(fall_conf)

                if self.consecutive_fall_frames >= self.required_fall_frames:
                    self.state = "FALL_DETECTED"
                    self.fall_start_time = now
                    self.total_falls += 1
                    self.consecutive_stand_frames = 0

                    if self.on_state_change:
                        self.on_state_change(self.state, now)

                    print("🚨 FALL DETECTED!")

            else:
                self.consecutive_fall_frames = max(0, self.consecutive_fall_frames - 1)

        elif self.state == "FALL_DETECTED":
            if stand_conf > 0.7:
                self.consecutive_stand_frames += 1
                if self.consecutive_stand_frames >= self.required_stand_frames:
                    self.state = "MONITORING"
                    self.consecutive_fall_frames = 0
                    self.fall_confidence_history.clear()

                    if self.on_state_change:
                        self.on_state_change(self.state, now)

    # ================= FRAME PROCESS =================
    def process_frame_fast(self, frame):
        resized = cv2.resize(frame, (640, 480))
        results = self.pose_model(resized, verbose=False, imgsz=320)

        fall_conf = 0.0
        stand_conf = 0.0
        keypoints = None

        if results and results[0].keypoints is not None:
            keypoints = results[0].keypoints.data.cpu().numpy()
            if len(keypoints) > 0:
                fall_conf = self.calculate_fall_confidence(keypoints, frame.shape)
                stand_conf = self.calculate_stand_confidence(keypoints)

        self.update_state_machine(fall_conf, stand_conf)
        return fall_conf, stand_conf, keypoints

    def draw_results(self, frame):
        color = (0, 255, 0) if self.state == "MONITORING" else (0, 0, 255)
        cv2.putText(frame, f"State: {self.state}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
