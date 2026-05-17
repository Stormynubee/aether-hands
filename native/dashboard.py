import customtkinter as ctk
import tkinter as tk

class AetherDashboard(ctk.CTk):
    def __init__(self, bridge=None):
        super().__init__()
        self.bridge = bridge

        # Ghost Style configuration
        self.width = 100
        self.height = self.winfo_screenheight()
        
        # Set window size and position (left edge)
        self.geometry(f"{self.width}x{self.height}+0+0")
        
        # Transparency and decorations
        self.attributes("-alpha", 0.8)
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        
        # Background color
        self.configure(fg_color="#0A0A0A") # Very dark grey

        # StatusPulse Canvas
        self.pulse_canvas = tk.Canvas(
            self, 
            width=20, 
            height=20, 
            bg="#0A0A0A", 
            highlightthickness=0
        )
        self.pulse_canvas.pack(pady=20)
        
        # Draw the circle
        self.pulse_circle = self.pulse_canvas.create_oval(
            4, 4, 16, 16, 
            fill="#008888", 
            outline=""
        )
        
        self.pulse_state = False
        self.update_pulse()
        
        # Camera Switch Button
        self.cam_button = ctk.CTkButton(
            self,
            text="CAM",
            width=60,
            height=30,
            fg_color="#008888",
            hover_color="#00AAAA",
            command=self.switch_camera
        )
        self.cam_button.pack(pady=10)

        # Gesture Feedback Container
        self.gesture_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.gesture_frame.pack(pady=20)

        self.gesture_labels = {}
        for code, label_text in [("PT", "PT"), ("PH", "PH"), ("FS", "FS")]:
            lbl = ctk.CTkLabel(
                self.gesture_frame,
                text=label_text,
                font=("Orbitron", 14, "bold"),
                text_color="#444444"
            )
            lbl.pack(pady=5)
            self.gesture_labels[code] = lbl

        # Transparency Slider Label
        self.slider_label = ctk.CTkLabel(
            self,
            text="ALPHA",
            font=("Orbitron", 10),
            text_color="#888888"
        )
        self.slider_label.pack(side="bottom", pady=(0, 5))

        # Transparency Slider
        self.alpha_slider = ctk.CTkSlider(
            self,
            from_=0.2,
            to=1.0,
            width=80,
            height=16,
            button_color="#008888",
            button_hover_color="#00AAAA",
            command=self.change_transparency
        )
        self.alpha_slider.set(0.8)
        self.alpha_slider.pack(side="bottom", pady=10)

        # Version Label
        self.version_label = ctk.CTkLabel(
            self,
            text="AETHER v2.0",
            font=("Orbitron", 8),
            text_color="#444444"
        )
        self.version_label.pack(side="bottom", pady=5)
        
        self.check_bridge()

    def change_transparency(self, value):
        """Changes the window transparency (alpha)."""
        self.attributes("-alpha", float(value))

    def highlight_gesture(self, gesture_code):
        """Highlights a gesture label and resets it after a delay."""
        if gesture_code in self.gesture_labels:
            lbl = self.gesture_labels[gesture_code]
            color = "#00FFFF" if gesture_code != "FS" else "#FF00FF"
            lbl.configure(text_color=color)
            self.after(200, lambda: lbl.configure(text_color="#444444"))

    def switch_camera(self):
        """Sends a switch camera command to the engine via the bridge."""
        if self.bridge:
            print("Dashboard: Requesting camera switch...")
            self.bridge.to_engine.put("switch_camera")

    def update_pulse(self):
        """Changes the circle color to create a pulse effect."""
        new_color = "#00FFFF" if self.pulse_state else "#008888"
        self.pulse_canvas.itemconfig(self.pulse_circle, fill=new_color)
        self.pulse_state = not self.pulse_state
        self.after(500, self.update_pulse)

    def check_bridge(self):
        """Polls the bridge for messages from the engine."""
        if self.bridge:
            try:
                while True:
                    msg = self.bridge.to_ui.get_nowait()
                    print(f"Dashboard received: {msg}")
                    
                    # Map bridge messages to gestures
                    if "Click" in msg or "Pinch" in msg:
                        self.highlight_gesture("PH")
                    elif "Point" in msg or "Cursor" in msg:
                        self.highlight_gesture("PT")
                    elif "Fist" in msg or "Minimize" in msg or "Volume" in msg:
                        self.highlight_gesture("FS")
            except: # Queue empty
                pass
        self.after(50, self.check_bridge)

if __name__ == "__main__":
    app = AetherDashboard()
    app.mainloop()
