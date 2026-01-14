import time
from collections import deque

class EmergencyDecisionEngine:
    def __init__(self):
        # --- FALL TRACKING ---
        self.fall_state = "MONITORING"
        self.fall_start_time = None

        # --- VOICE TRACKING ---
        self.voice_events = deque()  # stores timestamps of voice keywords

        # --- EMERGENCY STATE ---
        self.emergency_triggered = False

    # ================= FALL INPUT =================
    def update_fall_state(self, state: str, timestamp: float):
        """
        state: "FALL_DETECTED" or "MONITORING"
        """
        if state == "FALL_DETECTED":
            if self.fall_state != "FALL_DETECTED":
                self.fall_start_time = timestamp
        else:
            self.fall_start_time = None

        self.fall_state = state
        self.evaluate(timestamp)

    # ================= VOICE INPUT =================
    def register_voice_keyword(self, keyword: str, timestamp: float):
        self.voice_events.append(timestamp)
        self.cleanup_voice_events(timestamp)
        self.evaluate(timestamp)

    # ================= CORE LOGIC =================
    def cleanup_voice_events(self, now):
        # Keep only last 20 seconds
        while self.voice_events and now - self.voice_events[0] > 20:
            self.voice_events.popleft()

    def evaluate(self, now):
        if self.emergency_triggered:
            return  # fire only once

        # ---------- RULE 1 ----------
        if self.fall_state == "FALL_DETECTED" and self.fall_start_time:
            fall_duration = now - self.fall_start_time

            if fall_duration >= 10:
                self.trigger_emergency(
                    reason="Fall detected for ≥ 10 seconds"
                )
                return

        # ---------- RULE 2 ----------
        if self.fall_state == "FALL_DETECTED" and self.fall_start_time:
            fall_duration = now - self.fall_start_time

            if fall_duration >= 5 and len(self.voice_events) >= 1:
                self.trigger_emergency(
                    reason="Fall ≥ 5 seconds + voice emergency keyword"
                )
                return

        # ---------- RULE 3 ----------
        if len(self.voice_events) >= 2:
            self.trigger_emergency(
                reason="Voice emergency keyword repeated ≥ 2 times within 20 seconds"
            )
            return

    # ================= OUTPUT =================
    def trigger_emergency(self, reason):
        self.emergency_triggered = True
        print("\n" + "!" * 60)
        print("🚨🚨🚨 EMERGENCY CONFIRMED 🚨🚨🚨")
        print(f"Reason: {reason}")
        print(f"Time  : {time.strftime('%H:%M:%S')}")
        print("!" * 60 + "\n")
