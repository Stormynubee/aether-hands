import pyautogui
import math
import time

class AetherEngine:
    """
    Precision Engine with Suppressed Accidental Pinches.
    """
    def __init__(self, screen_width, screen_height, alpha=0.3, bridge=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.alpha = alpha
        self.bridge = bridge
        
        self.prev_x = screen_width // 2
        self.prev_y = screen_height // 2
        
        self.pinch_active = False
        self.pinky_active = False
        self.gesture_cooldown = 0
        
        self.pinch_threshold = 0.035 # Slightly tighter threshold
        pyautogui.PAUSE = 0

    def _get_distance(self, p1, p2):
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

    def update(self, landmarks, bridge=None):
        if bridge:
            self.bridge = bridge

        if not landmarks or len(landmarks) < 21:
            return

        curr_time = time.time()
        
        # 1. MOUSE CONTROL
        index_tip = landmarks[8]
        raw_x = index_tip.x * self.screen_width
        raw_y = index_tip.y * self.screen_height
        
        smoothed_x = (self.alpha * raw_x) + (1 - self.alpha) * self.prev_x
        smoothed_y = (self.alpha * raw_y) + (1 - self.alpha) * self.prev_y
        
        try:
            pyautogui.moveTo(int(smoothed_x), int(smoothed_y))
        except: pass
            
        self.prev_x, self.prev_y = smoothed_x, smoothed_y

        # 2. GESTURE PROCESSING
        if curr_time > self.gesture_cooldown:
            
            # FINGER STATE ANALYSIS
            # Tip Y significantly above PIP joint Y
            index_up = landmarks[8].y < landmarks[6].y - 0.02
            middle_up = landmarks[12].y < landmarks[10].y - 0.02
            ring_up = landmarks[16].y < landmarks[14].y - 0.02
            pinky_up = landmarks[20].y < landmarks[18].y - 0.02
            
            thumb_tip = landmarks[4]
            thumb_is_up = thumb_tip.y < landmarks[3].y - 0.03
            thumb_is_down = thumb_tip.y > landmarks[3].y + 0.03

            # A. PINCH (Index + Thumb) -> Click
            # CRITICAL FIX: Only allow pinch if Index is also extended/pointing.
            # If Index is folded (index_up is False), it's likely a Thumb gesture, so we SUPPRESS the pinch.
            if index_up:
                pinch_dist = self._get_distance(thumb_tip, index_tip)
                if pinch_dist < self.pinch_threshold:
                    if not self.pinch_active:
                        pyautogui.click()
                        self.pinch_active = True
                        print("Action: Click")
                        if self.bridge:
                            self.bridge.to_ui.put({"type": "gesture", "value": "Click"})
                    return 
            
            self.pinch_active = False

            # B. MINIMIZE -> ONLY Pinky is Up (No Thumb)
            if pinky_up and not index_up and not middle_up and not ring_up and not thumb_is_up:
                if not self.pinky_active:
                    pyautogui.hotkey('win', 'down')
                    self.pinky_active = True
                    print("Action: Minimize")
                    if self.bridge:
                        self.bridge.to_ui.put({"type": "gesture", "value": "Minimize"})
                    self.gesture_cooldown = curr_time + 1.2
                return
            else:
                self.pinky_active = False

            # C. VOLUME -> Thumb gestures (Others must be closed)
            others_closed = not index_up and not middle_up and not ring_up and not pinky_up
            
            if others_closed:
                if thumb_is_up:
                    pyautogui.press('volumeup', presses=2)
                    print("Action: Volume UP 👍")
                    if self.bridge:
                        self.bridge.to_ui.put({"type": "gesture", "value": "Volume UP"})
                    self.gesture_cooldown = curr_time + 0.3
                elif thumb_is_down:
                    pyautogui.press('volumedown', presses=2)
                    print("Action: Volume DOWN 👎")
                    if self.bridge:
                        self.bridge.to_ui.put({"type": "gesture", "value": "Volume DOWN"})
                    self.gesture_cooldown = curr_time + 0.3
