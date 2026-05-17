import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
import time
import os
import threading
from engine import AetherEngine
from hud import GhostHUD
from bridge import AetherBridge
from dashboard import AetherDashboard

def run_vision_loop(bridge):
    """
    Vision processing loop running in a separate thread.
    Handles OpenCV capture, MediaPipe detection, and HUD updates.
    """
    screen_width, screen_height = pyautogui.size()
    engine = AetherEngine(screen_width, screen_height, alpha=0.3, bridge=bridge)
    hud = GhostHUD()
    
    show_debug = True
    current_camera_index = 0
    
    model_path = os.path.join(os.path.dirname(__file__), 'hand_landmarker.task')
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}")
        return

    def create_detector():
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.7,
            min_tracking_confidence=0.7
        )
        return vision.HandLandmarker.create_from_options(options)

    detector = create_detector()
    cap = cv2.VideoCapture(current_camera_index)
    
    print(f"\nVision Loop Active on Camera {current_camera_index}")
    
    try:
        while True:
            # Check for messages from the Bridge (UI -> Engine)
            try:
                msg = bridge.to_engine.get_nowait()
                if msg == "switch_camera":
                    current_camera_index += 1
                    print(f"Switching to camera index: {current_camera_index}")
                    cap.release()
                    cv2.destroyAllWindows()
                    cap = cv2.VideoCapture(current_camera_index)
                    if not cap.isOpened():
                        print(f"Camera {current_camera_index} not found. Resetting to 0.")
                        current_camera_index = 0
                        cap = cv2.VideoCapture(current_camera_index)
                    time.sleep(0.5)
                elif msg == "toggle_debug":
                    show_debug = not show_debug
                    if not show_debug:
                        cv2.destroyAllWindows()
            except: # Queue empty
                pass

            success, frame = cap.read()
            if not success:
                time.sleep(0.1)
                continue
                
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            timestamp_ms = int(time.time() * 1000)
            result = detector.detect_for_video(mp_image, timestamp_ms)
            
            hud_points = []
            if result.hand_landmarks:
                landmarks = result.hand_landmarks[0]
                engine.update(landmarks, bridge=bridge)
                
                for lm in landmarks:
                    hud_points.append((int(lm.x * screen_width), int(lm.y * screen_height)))
                
                if show_debug:
                    h, w, _ = frame.shape
                    for lm in landmarks:
                        cv2.circle(frame, (int(lm.x * w), int(lm.y * h)), 5, (255, 0, 255), -1)
            
            # Draw landmarks on the GhostHUD (running in this thread's Tk instance)
            hud.draw_landmarks(hud_points)
            
            if show_debug:
                cv2.imshow('Aether Debug (C=Switch, D=Hide, ESC=Quit)', frame)
            
            # Update the HUD window
            if not hud.update():
                break
                
            # Process OpenCV events and handle local keyboard shortcuts
            key = cv2.waitKey(1) & 0xFF
            if key == 27: # ESC
                break
            elif key == ord('d'):
                show_debug = not show_debug
                if not show_debug: cv2.destroyAllWindows()
            elif key == ord('c'):
                bridge.to_engine.put("switch_camera")

    except Exception as e:
        print(f"\nVision Loop Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.close()
        print("Vision Loop stopped.")

def main():
    """
    Main entry point for Aether Hands v2.
    Starts the vision thread and runs the dashboard mainloop.
    """
    print("\n--- Aether Hands v2 Initialization ---")
    
    # 1. Initialize Bridge
    bridge = AetherBridge()
    
    # 2. Start Vision Thread
    vision_thread = threading.Thread(
        target=run_vision_loop, 
        args=(bridge,), 
        daemon=True
    )
    vision_thread.start()
    
    # 3. Initialize and Run Dashboard (Main Thread)
    print("Launching Aether Dashboard...")
    app = AetherDashboard(bridge)
    app.mainloop()

if __name__ == "__main__":
    main()
