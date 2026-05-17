import queue

class AetherBridge:
    def __init__(self):
        self.to_ui = queue.Queue() # For Gestures, FPS, Status updates
        self.to_engine = queue.Queue() # For Commands from UI (switch cam, etc.)
