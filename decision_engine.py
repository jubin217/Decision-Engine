import time
from collections import deque
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os

class EmergencyDecisionEngine:
    def __init__(self, emergency_flag=None):
        # --- FIREBASE SETUP ---
        self.db = self._init_firebase()

        # --- SHARED STATE ---
        self.emergency_flag = emergency_flag

        # --- FALL TRACKING ---
        self.fall_state = "MONITORING"
        self.fall_start_time = None

        # --- VOICE TRACKING ---
        self.voice_events = deque()  # stores timestamps of voice keywords
        self.last_voice_time = 0

        # --- EMERGENCY STATE ---
        self.emergency_triggered = False

    # ================= FALL INPUT =================
    def update_fall_state(self, state: str, timestamp: float):
        if state == "CAMERA_ACTIVE":
            print("🟢 Fall system ACTIVE (camera + model running)")
            self.fall_state = "MONITORING"
            return
            
        if state != self.fall_state:
            print(f"🔄 State change: {self.fall_state} -> {state}")
            self.fall_state = state
            
            if state == "FALL_DETECTED":
                self.fall_start_time = timestamp
            elif state == "MONITORING":
                self.fall_start_time = None
        
        # Always evaluate after a state update
        self.evaluate(timestamp)


    # ================= VOICE INPUT =================
    def register_voice_keyword(self, keyword: str, timestamp: float):
        # Debounce: Ignore duplicate keywords within 1 second
        if timestamp - self.last_voice_time < 1.0:
            print(f"⏳ Ignoring duplicate voice event ({keyword})")
            return
            
        self.last_voice_time = timestamp
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
        if len(self.voice_events) >= 3:
            self.trigger_emergency(
                reason="Voice emergency keyword repeated ≥ 3 times within 20 seconds"
            )
            return

    def _init_firebase(self):
        try:
            # Check if already initialized
            if not firebase_admin._apps:
                # We need a service account key. 
                # For now, we'll look for 'service_account.json' in the current directory.
                key_path = os.path.join(os.getcwd(), 'service_account.json')
                if os.path.exists(key_path):
                    cred = credentials.Certificate(key_path)
                    firebase_admin.initialize_app(cred)
                    print("🔥 Firebase Admin initialized successfully.")
                else:
                    print("⚠️ Firebase Service Account key (serviceAccountKey.json) not found. Cloud syncing DISABLED.")
                    return None
            return firestore.client()
        except Exception as e:
            print(f"❌ Error initializing Firebase: {e}")
            return None

    def push_to_firestore(self, reason):
        if not self.db:
            return
        
        try:
            doc_ref = self.db.collection('emergencies').document()
            doc_ref.set({
                'reason': reason,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'type': 'CRITICAL',
                'location': 'Living Room' # Placeholder or dynamic if available
            })
            print(f"✅ Emergency logged to Firestore (ID: {doc_ref.id})")
        except Exception as e:
            print(f"❌ Failed to sync with Firestore: {e}")

    # ================= OUTPUT =================
    def trigger_emergency(self, reason):
        self.emergency_triggered = True
        
        # Set shared flag if available
        if self.emergency_flag:
            self.emergency_flag.value = True
        
        # Sync to Cloud
        self.push_to_firestore(reason)
            
        print("\n" + "!" * 60)
        print("🚨🚨🚨 EMERGENCY CONFIRMED 🚨🚨🚨")
        print(f"Reason: {reason}")
        print(f"Time  : {time.strftime('%H:%M:%S')}")
        print("!" * 60 + "\n")

    def emergency_complete(self):
       self.emergency_active = False
       self.voice_history.clear()
       print("🟢 Emergency state reset")

