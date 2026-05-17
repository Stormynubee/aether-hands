from fastapi import FastAPI, WebSocket
import pyautogui
import json
import math

app = FastAPI()

# Disable pyautogui fail-safe for a smoother experience (optional, but be careful)
pyautogui.FAILSAFE = True
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Simple smoothing variables
last_x, last_y = 0, 0
smoothing = 0.5

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global last_x, last_y
    await websocket.accept()
    print("Client connected")
    
    while True:
        try:
            message = await websocket.receive_text()
            data = json.loads(message)
            gesture_type = data.get("type")

            if gesture_type == "point":
                # MediaPipe coordinates are normalized 0-1
                # We need to mirror the X coordinate because the camera is mirrored
                target_x = (1 - data["x"]) * SCREEN_WIDTH
                target_y = data["y"] * SCREEN_HEIGHT

                # Apply smoothing
                curr_x = last_x + (target_x - last_x) * smoothing
                curr_y = last_y + (target_y - last_y) * smoothing
                
                pyautogui.moveTo(curr_x, curr_y, _pause=False)
                last_x, last_y = curr_x, curr_y

            elif gesture_type == "pinch":
                pyautogui.click()
                print("Action: Click")

            elif gesture_type == "swipe_right":
                pyautogui.hotkey('alt', 'tab')
                print("Action: Alt+Tab")

            elif gesture_type == "fist":
                pyautogui.hotkey('win', 'down')
                print("Action: Minimize")

        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
