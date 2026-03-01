import cv2
import sys

def test_cameras():
    print("--- Camera Diagnostic Tool ---")
    
    # Try different backends
    backends = [
        ("Default", None),
        ("DSHOW", cv2.CAP_DSHOW),
        ("MSMF", cv2.CAP_MSMF),
    ]
    
    found_any = False
    
    for backend_name, backend_id in backends:
        print(f"\nTesting with backend: {backend_name}")
        for i in range(3):
            print(f"  Attempting index {i}...", end=" ", flush=True)
            if backend_id is not None:
                cap = cv2.VideoCapture(i, backend_id)
            else:
                cap = cv2.VideoCapture(i)
                
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    print(f"SUCCESS! ({int(w)}x{int(h)})")
                    found_any = True
                else:
                    print("Opened but failed to read frame.")
                cap.release()
            else:
                print("Failed to open.")
                
    if not found_any:
        print("\n!!! NO WORKING CAMERAS FOUND !!!")
        print("Suggestions: Check physical connection, drivers, or privacy settings.")
    else:
        print("\n--- Diagnostic Complete ---")

if __name__ == "__main__":
    test_cameras()
