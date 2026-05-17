# Aether Hands v2.0

**Aether Hands** is a high-performance, native system utility for gesture-based computer control. It uses MediaPipe's hand tracking to translate physical hand movements into system actions like mouse movement, clicking, window management, and volume control—all through a sleek, cyberpunk-inspired "Ghost HUD" dashboard.

## 🚀 Key Features

- **Ghost Sidebar Dashboard:** A native, semi-transparent vertical dashboard built with CustomTkinter that docks to the screen edge.
- **Precision Vision Engine:** Multi-threaded MediaPipe integration for ultra-low latency tracking.
- **Interactive HUD:** Real-time visual feedback for detected gestures.
- **Dynamic Camera Switching:** Effortlessly cycle through available cameras directly from the UI.
- **Native Integration:** Built-in support for Windows system controls via PyAutoGUI and Win32 API.

## 🖐️ Gesture Bindings

| Gesture | Action | UI Label |
| :--- | :--- | :--- |
| **Point (Index Extended)** | Mouse Movement | `PT` |
| **Pinch (Index + Thumb)** | Left Click | `PH` |
| **Pinky Up** | Minimize Window | `FS` (Special) |
| **Thumb Up / Down** | Volume Control | `FS` (Special) |

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Stormynubee/aether-hands.git
   cd aether-hands
   ```

2. **Install dependencies:**
   ```bash
   pip install -r native/requirements.txt
   ```

3. **Run the application:**
   ```bash
   python native/main.py
   ```

## ⚙️ Requirements

- Python 3.9+
- Webcam
- Windows (for full native integration features)

## 📦 Tech Stack

- **UI:** CustomTkinter, Tkinter, PyWin32
- **Vision:** MediaPipe, OpenCV
- **Automation:** PyAutoGUI

---
*Built with ❤️ by Stormynubee*
