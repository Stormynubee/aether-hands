import tkinter as tk
import win32gui
import win32con
import win32api
import ctypes

class GhostHUD:
    """
    A transparent, click-through overlay window for Aether Hands.
    Uses Tkinter for rendering and Win32 API for click-through behavior.
    """
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Aether Ghost HUD")
        
        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Configure window: full screen, topmost, no decorations
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        # Use a specific color for transparency (avoiding pure black which might be used elsewhere)
        self.trans_color = "#010101" 
        self.root.config(bg=self.trans_color)
        self.root.wm_attributes("-transparentcolor", self.trans_color)
        
        # Create Canvas covering the full screen
        self.canvas = tk.Canvas(
            self.root, 
            width=self.screen_width, 
            height=self.screen_height, 
            bg=self.trans_color, 
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Bind Escape key to close the HUD
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # Force an initial update to ensure the window is created and mapped
        self.root.update()

        # Apply Windows-specific styles for click-through behavior
        self.make_click_through()
        
        # Initial draw of static elements
        self._draw_static_hud()

    def make_click_through(self):
        """Sets the window style to be click-through using Win32 API."""
        try:
            # Find the window handle more reliably
            hwnd = win32gui.FindWindow(None, "Aether Ghost HUD")
            if not hwnd:
                hwnd = self.root.winfo_id()

            # GWL_EXSTYLE: Set extended window styles
            # WS_EX_TRANSPARENT: Clicks pass through
            # WS_EX_LAYERED: Required for transparency
            styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            new_styles = styles | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_styles)
            
            # Additional safety: ensure the window is truly on top
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0,0,0,0, 
                                 win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        except Exception as e:
            print(f"Warning: Could not set click-through styles: {e}")

    def draw_landmarks(self, landmarks):
        """
        Draws a list of landmarks on the canvas.
        landmarks: List of tuples (x, y) in pixel coordinates.
        """
        self.canvas.delete("skeleton")
        
        if not landmarks:
            return

        # Hand connection indices
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (5, 9), (9, 10), (10, 11), (11, 12),
            (9, 13), (13, 14), (14, 15), (15, 16),
            (13, 17), (17, 18), (18, 19), (19, 20),
            (0, 17)
        ]

        # Draw skeleton lines (Industrial Amber)
        for start_idx, end_idx in connections:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                x1, y1 = landmarks[start_idx]
                x2, y2 = landmarks[end_idx]
                self.canvas.create_line(
                    x1, y1, x2, y2, 
                    fill="#FF9500", 
                    width=2, 
                    tags="skeleton"
                )

        # Draw landmarks as Magenta circles
        for x, y in landmarks:
            radius = 3
            try:
                self.canvas.create_oval(
                    x - radius, y - radius, 
                    x + radius, y + radius, 
                    fill="#FF00FF", 
                    outline="#FF00FF",
                    width=1,
                    tags="skeleton"
                )
            except Exception:
                pass

    def _draw_static_hud(self):
        """Draws the persistent HUD elements."""
        margin = 40
        length = 60
        color = "#FF9500"
        
        # Scanlines (HUD v2)
        # Drawing ~270 lines for 1080p is fine for performance
        for y in range(0, self.screen_height, 4):
            self.canvas.create_line(
                0, y, self.screen_width, y, 
                fill="#111111", 
                stipple="gray12",
                tags="static"
            )

        # Brackets
        self.canvas.create_line(margin, margin, margin + length, margin, fill=color, width=4, tags="static")
        self.canvas.create_line(margin, margin, margin, margin + length, fill=color, width=4, tags="static")
        self.canvas.create_line(self.screen_width - margin, margin, self.screen_width - margin - length, margin, fill=color, width=4, tags="static")
        self.canvas.create_line(self.screen_width - margin, margin, self.screen_width - margin, margin + length, fill=color, width=4, tags="static")
        self.canvas.create_line(margin, self.screen_height - margin, margin + length, self.screen_height - margin, fill=color, width=4, tags="static")
        self.canvas.create_line(margin, self.screen_height - margin, margin, self.screen_height - margin - length, fill=color, width=4, tags="static")
        self.canvas.create_line(self.screen_width - margin, self.screen_height - margin, self.screen_width - margin - length, self.screen_height - margin, fill=color, width=4, tags="static")
        self.canvas.create_line(self.screen_width - margin, self.screen_height - margin, self.screen_width - margin, self.screen_height - margin - length, fill=color, width=4, tags="static")

        self.canvas.create_text(
            margin + 10, margin + 20,
            text="AETHER VISION ACTIVE",
            fill=color,
            font=("Courier", 12, "bold"),
            anchor="nw",
            tags="static"
        )

    def update(self):
        """Refreshes the HUD window."""
        try:
            self.root.update_idletasks()
            self.root.update()
            return True
        except Exception:
            return False

if __name__ == "__main__":
    # Test
    hud = GhostHUD()
    while hud.update():
        import time
        time.sleep(0.01)
