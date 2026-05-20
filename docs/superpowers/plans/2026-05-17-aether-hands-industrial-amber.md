# Aether Hands: Industrial Amber Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform Aether Hands into a Tech-Brutalist utility with an Industrial Amber aesthetic, enhanced controls, and a stylized Ghost HUD.

**Architecture:** A native Python/CustomTkinter dashboard manages state and camera parameters, communicating with a multi-threaded Vision Engine and transparent HUD overlay via a thread-safe Bridge.

**Tech Stack:** Python, CustomTkinter, OpenCV, MediaPipe, PyWin32, PyAutoGUI.

---

### Task 1: Theme Migration (Amber-on-Black)

**Files:**
- Modify: `native/dashboard.py`
- Modify: `native/hud.py`

- [ ] **Step 1: Update Dashboard Colors**
Change `fg_color` and status colors to Amber (#FF9500).
```python
# In native/dashboard.py
self.configure(fg_color="#050505")
# Update buttons and sliders to #FF9500
```

- [ ] **Step 2: Update HUD Colors**
Change skeleton and text colors to Amber (#FF9500) and Magenta (#FF00FF).
```python
# In native/hud.py
color = "#FF9500"
# Update drawing logic...
```

- [ ] **Step 3: Verify Visuals**
Run: `python native/main.py`
Expected: UI elements are Amber, HUD skeleton is Amber.

- [ ] **Step 4: Commit**
```bash
git add native/dashboard.py native/hud.py
git commit -m "style: migrate to industrial amber theme"
```

---

### Task 2: Dashboard Control Expansion

**Files:**
- Modify: `native/dashboard.py`
- Modify: `native/bridge.py`

- [ ] **Step 1: Replace CAM Button with PREV/NEXT**
Update `AetherDashboard` to use dual buttons for camera navigation.
```python
# In native/dashboard.py
self.prev_btn = ctk.CTkButton(self, text="PREV", command=lambda: self.switch_cam(-1))
self.next_btn = ctk.CTkButton(self, text="NEXT", command=lambda: self.switch_cam(1))
```

- [ ] **Step 2: Add Parameter Sliders**
Implement "SMOOTH" and "PINCH" sliders.
```python
# In native/dashboard.py
self.smooth_slider = ctk.CTkSlider(self, from_=0.0, to=1.0, command=self.update_params)
self.pinch_slider = ctk.CTkSlider(self, from_=0.01, to=0.1, command=self.update_params)
```

- [ ] **Step 3: Update Bridge for Parameters**
Ensure `AetherBridge` can handle parameter updates.
```python
# In native/bridge.py
# No changes needed if using to_engine.put({"type": "param", "key": "...", "val": ...})
```

- [ ] **Step 4: Verify Controls**
Run: `python native/dashboard.py`
Expected: Sliders and dual buttons visible and responsive.

- [ ] **Step 5: Commit**
```bash
git add native/dashboard.py
git commit -m "feat: add camera nav and parameter sliders to dashboard"
```

---

### Task 3: HUD v2 Stylization

**Files:**
- Modify: `native/hud.py`

- [ ] **Step 1: Add Thick Corner Brackets**
Update `_draw_static_hud` to draw 4px thick brackets.
```python
# In native/hud.py
def _draw_static_hud(self):
    # Draw thicker L-shaped brackets...
```

- [ ] **Step 2: Implement Scanline Overlay**
Draw a series of horizontal lines with low alpha.
```python
# In native/hud.py
for y in range(0, self.screen_height, 4):
    self.canvas.create_line(0, y, self.screen_width, y, fill="#222", stipple="gray25")
```

- [ ] **Step 3: Verify HUD Style**
Run: `python native/hud.py` (direct test)
Expected: Visible corner brackets and scanline effect.

- [ ] **Step 4: Commit**
```bash
git add native/hud.py
git commit -m "style: implement HUD v2 brackets and scanlines"
```

---

### Task 4: Engine Parameter Bridging

**Files:**
- Modify: `native/main.py`
- Modify: `native/engine.py`

- [ ] **Step 1: Handle Parameter Messages in Vision Loop**
Update `run_vision_loop` to process slider updates.
```python
# In native/main.py
if msg["type"] == "param":
    engine.set_param(msg["key"], msg["val"])
```

- [ ] **Step 2: Implement Engine Parameter Updates**
Add a setter to `AetherEngine`.
```python
# In native/engine.py
def set_param(self, key, val):
    if key == "smoothing": self.alpha = val
    elif key == "pinch": self.pinch_threshold = val
```

- [ ] **Step 3: Final System Integration Test**
Run: `python native/main.py`
Expected: Adjusting sliders in the Dashboard changes tracking behavior in real-time.

- [ ] **Step 4: Commit**
```bash
git add native/main.py native/engine.py
git commit -m "feat: bridge dashboard sliders to aether engine"
```
