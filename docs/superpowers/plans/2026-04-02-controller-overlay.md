# Game Controller Overlay - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a lightweight Windows desktop overlay that shows real-time game controller button/joystick feedback via a transparent, click-through, always-on-top window controlled from a system tray icon.

**Architecture:** Single-thread Python app. QTimer polls SDL2 for gamepad state at ~120Hz on the PyQt5 main thread. Results feed directly into QPainter redraw of the overlay. System tray icon provides the only user-facing settings UI.

**Tech Stack:** Python 3.10+, PyQt5, PySDL2, ctypes (Win32 API for click-through), PyInstaller (packaging)

---

## File Structure

```
d:\ControllerMapping\
├── main.py              # Entry point: init SDL2, Qt, create overlay + tray
├── gamepad.py           # SDL2 joystick abstraction (detect, poll, map)
├── overlay.py           # Transparent overlay window with QPainter controller
├── tray.py              # System tray icon + context menu
├── themes.py            # Color theme definitions
├── requirements.txt     # Dependencies
├── .gitignore
└── tests/
    ├── test_themes.py
    └── test_gamepad.py
```

---

### Task 1: Project Bootstrap

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```
PyQt5>=5.15
PySDL2>=0.9
```

- [ ] **Step 2: Create .gitignore**

```
__pycache__/
*.pyc
*.spec
build/
dist/
*.exe
.superpowers/
```

- [ ] **Step 3: Create tests/__init__.py**

Empty file.

- [ ] **Step 4: Install dependencies**

Run: `pip install PyQt5 PySDL2`

Expected: Both packages install successfully.

- [ ] **Step 5: Initialize git and commit**

```bash
cd d:\ControllerMapping
git init
git add requirements.txt .gitignore tests/__init__.py
git commit -m "chore: project bootstrap with dependencies"
```

---

### Task 2: Color Themes Module

**Files:**
- Create: `themes.py`
- Create: `tests/test_themes.py`

This module is pure data — no GUI, no SDL2. Easy to test first.

- [ ] **Step 1: Write the test**

```python
# tests/test_themes.py
import pytest
from themes import THEMES, Theme


def test_all_themes_have_required_fields():
    for name, theme in THEMES.items():
        assert isinstance(theme, Theme)
        assert len(theme.body_fill) == 7  # "#RRGGBB"
        assert len(theme.outline) == 7
        assert len(theme.btn_default) == 7
        for btn in ("a", "b", "x", "y", "lb", "rb", "lt", "rt",
                     "dpad", "ls", "rs", "start", "back", "guide"):
            assert btn in theme.highlight, f"Missing highlight for {btn} in {name}"


def test_three_themes_exist():
    assert set(THEMES.keys()) == {"white", "black", "neon"}


def test_highlight_colors_are_valid_hex():
    for name, theme in THEMES.items():
        for btn, color in theme.highlight.items():
            assert color.startswith("#"), f"{name}.{btn} highlight not hex"
            assert len(color) == 7, f"{name}.{btn} highlight wrong length"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_themes.py -v`
Expected: FAIL — `cannot import 'themes'`

- [ ] **Step 3: Write themes.py**

```python
from dataclasses import dataclass, field


@dataclass
class Theme:
    body_fill: str
    outline: str
    btn_default: str
    highlight: dict  # button_name -> color_hex


def _xbox_colors(base):
    """Standard Xbox ABXY colors (green, red, blue, yellow)."""
    return {
        "a": "#2ECC71" if base == "light" else "#3DFF8F" if base == "dark" else "#00FFAA",
        "b": "#E74C3C" if base == "light" else "#FF4D6A" if base == "dark" else "#FF0066",
        "x": "#3498FF" if base == "light" else "#5CB8FF" if base == "dark" else "#00AAFF",
        "y": "#F1C40F" if base == "light" else "#FFE04D" if base == "dark" else "#FFD700",
    }


def _make_theme(body, outline, btn_default, base):
    colors = _xbox_colors(base)
    return Theme(
        body_fill=body,
        outline=outline,
        btn_default=btn_default,
        highlight={
            "a": colors["a"], "b": colors["b"], "x": colors["x"], "y": colors["y"],
            "lb": colors["b"], "rb": colors["x"],
            "lt": colors["b"], "rt": colors["x"],
            "dpad": outline, "ls": colors["x"], "rs": colors["a"],
            "start": colors["a"], "back": colors["b"], "guide": colors["y"],
        },
    )


THEMES = {
    "white": _make_theme("#E8E8E8", "#999999", "#CCCCCC", "light"),
    "black": _make_theme("#2A2A2A", "#666666", "#555555", "dark"),
    "neon":  _make_theme("#1A1A2E", "#4A4AFF", "#333366", "neon"),
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_themes.py -v`
Expected: 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add themes.py tests/test_themes.py
git commit -m "feat: add color theme definitions (white/black/neon)"
```

---

### Task 3: Gamepad Input Module

**Files:**
- Create: `gamepad.py`
- Create: `tests/test_gamepad.py`

This module wraps SDL2 joystick APIs. The mapping logic is testable without hardware.

- [ ] **Step 1: Write the test**

```python
# tests/test_gamepad.py
from gamepad import normalize_axis, DEADZONE_PERCENT, AXIS_MAX


def test_normalize_axis_center():
    """Center position (0) should normalize to 0."""
    assert normalize_axis(0) == 0.0


def test_normalize_axis_full_right():
    """Full right/down should normalize to ~1.0."""
    result = normalize_axis(AXIS_MAX)
    assert abs(result - 1.0) < 0.01


def test_normalize_axis_full_left():
    """Full left/up should normalize to ~-1.0."""
    result = normalize_axis(-AXIS_MAX)
    assert abs(result - (-1.0)) < 0.01


def test_normalize_axis_deadzone_center_region():
    """Values within deadzone should return 0."""
    threshold = int(AXIS_MAX * DEADZONE_PERCENT)
    assert normalize_axis(threshold - 1) == 0.0
    assert normalize_axis(-(threshold - 1)) == 0.0
    assert normalize_axis(threshold) != 0.0


def test_normalize_axis_deadzone_rescales():
    """Value just outside deadzone should be close to 0."""
    threshold = int(AXIS_MAX * DEADZONE_PERCENT)
    result = normalize_axis(threshold + 100)
    assert 0.0 < result < 0.1


def test_button_mapping_keys():
    """Verify all expected buttons exist in the mapping."""
    from gamepad import BUTTON_MAP, AXIS_MAP
    assert "a" in BUTTON_MAP
    assert "b" in BUTTON_MAP
    assert "x" in BUTTON_MAP
    assert "y" in BUTTON_MAP
    assert "lb" in BUTTON_MAP
    assert "rb" in BUTTON_MAP
    assert "start" in BUTTON_MAP
    assert "back" in BUTTON_MAP
    assert "guide" in BUTTON_MAP
    assert "ls_x" in AXIS_MAP
    assert "ls_y" in AXIS_MAP
    assert "rs_x" in AXIS_MAP
    assert "rs_y" in AXIS_MAP
    assert "lt" in AXIS_MAP
    assert "rt" in AXIS_MAP
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_gamepad.py -v`
Expected: FAIL — `cannot import 'gamepad'`

- [ ] **Step 3: Write gamepad.py**

```python
import sdl2

DEADZONE_PERCENT = 0.05
AXIS_MAX = 32767

# SDL2 button index -> our logical name
BUTTON_MAP = {
    "a": 0, "b": 1, "x": 2, "y": 3,
    "lb": 4, "rb": 5,
    "back": 6, "start": 7, "guide": 8,
}

# Our logical name -> (sdl_axis_index, is_positive)
# For triggers (LT/RT), SDL2 axis value > 0 means pressed
# For sticks, value represents position (-32768 to 32767)
AXIS_MAP = {
    "ls_x": 0, "ls_y": 1,
    "rs_x": 2, "rs_y": 3,
    "lt": 4, "rt": 5,
}

HAT_MAP = {
    "dpad": 0,
}


def normalize_axis(value):
    """Normalize a raw SDL2 axis value to [-1.0, 1.0] with deadzone applied."""
    threshold = int(AXIS_MAX * DEADZONE_PERCENT)
    if -threshold <= value <= threshold:
        return 0.0
    if value > threshold:
        return (value - threshold) / (AXIS_MAX - threshold)
    else:
        return (value + threshold) / (AXIS_MAX - threshold)


class GamepadState:
    """Snapshot of all gamepad inputs at a point in time."""

    def __init__(self):
        self.buttons = {name: False for name in BUTTON_MAP}
        self.axes = {name: 0.0 for name in AXIS_MAP}
        self.hats = {name: (0, 0) for name in HAT_MAP}
        self.connected = False
        self.name = ""


class GamepadManager:
    """Manages SDL2 joystick detection and state polling."""

    def __init__(self):
        self._joystick = None
        self._device_index = -1
        self.state = GamepadState()

    def init_sdl(self):
        """Initialize SDL2 joystick subsystem. Returns True on success."""
        ret = sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)
        if ret < 0:
            return False
        # Try to open first available joystick
        num = sdl2.SDL_NumJoysticks()
        if num > 0:
            self._open(0)
        return True

    def _open(self, index):
        """Open joystick at given device index."""
        js = sdl2.SDL_JoystickOpen(index)
        if js:
            self._joystick = js
            self._device_index = index
            self.state.connected = True
            name_bytes = sdl2.SDL_JoystickName(js)
            self.state.name = name_bytes.decode("utf-8", errors="replace") if name_bytes else f"Gamepad {index}"

    def close(self):
        """Close current joystick and quit SDL."""
        if self._joystick:
            sdl2.SDL_JoystickClose(self._joystick)
            self._joystick = None
        self.state.connected = False
        sdl2.SDL_Quit()

    def poll(self):
        """Poll SDL events and read current joystick state.

        Returns the updated GamepadState.
        """
        sdl2.SDL_PumpEvents()

        # Check for device change events
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(event):
            if event.type == sdl2.SDL_JOYDEVICEADDED:
                if not self.state.connected:
                    self._open(event.jdevice.which)
            elif event.type == sdl2.SDL_JOYDEVICEREMOVED:
                if self._joystick and sdl2.SDL_JoystickInstanceID(self._joystick) == event.jdevice.which:
                    sdl2.SDL_JoystickClose(self._joystick)
                    self._joystick = None
                    self.state.connected = False
                    self.state.name = ""

        # Read current state
        if not self._joystick:
            return self.state

        for name, idx in BUTTON_MAP.items():
            self.state.buttons[name] = bool(sdl2.SDL_JoystickGetButton(self._joystick, idx))

        for name, idx in AXIS_MAP.items():
            raw = sdl2.SDL_JoystickGetAxis(self._joystick, idx)
            self.state.axes[name] = normalize_axis(raw)

        for name, idx in HAT_MAP.items():
            hat_val = sdl2.SDL_JoystickGetHat(self._joystick, idx)
            # SDL_HAT values: SDL_HAT_UP=1, RIGHT=2, DOWN=4, LEFT=8
            x = 0
            y = 0
            if hat_val & sdl2.SDL_HAT_UP:
                y = -1
            if hat_val & sdl2.SDL_HAT_DOWN:
                y = 1
            if hat_val & sdl2.SDL_HAT_LEFT:
                x = -1
            if hat_val & sdl2.SDL_HAT_RIGHT:
                x = 1
            self.state.hats[name] = (x, y)

        return self.state
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_gamepad.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add gamepad.py tests/test_gamepad.py
git commit -m "feat: add gamepad input module with SDL2 polling"
```

---

### Task 4: Transparent Overlay Window

**Files:**
- Create: `overlay.py`

This is the core visual component. QPainter draws the controller from code. No external images needed.

- [ ] **Step 1: Write overlay.py**

```python
import ctypes
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QFont

import sdl2

from gamepad import GamepadManager
from themes import Theme

# Win32 constants for click-through
GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
WS_EX_LAYERED = 0x00080000

# Controller element positions (within 300x220 widget)
# All coordinates are (center_x, center_y) unless noted
LAYOUT = {
    "body": (20, 25, 280, 190),       # (x, y, w, h) rounded rect
    "lt": (42, 10, 68, 16),            # trigger rect
    "rt": (190, 10, 68, 16),
    "lb": (38, 28, 75, 16),            # bumper rect
    "rb": (187, 28, 75, 16),
    "guide": (150, 52, 10),            # (cx, cy, radius)
    "back": (125, 72, 7),
    "start": (175, 72, 7),
    "ls": (85, 95, 24),                # stick base (cx, cy, radius)
    "rs": (215, 135, 24),
    "ls_dot": (85, 95, 10),            # stick thumb (cx, cy, radius)
    "rs_dot": (215, 135, 10),
    "dpad_cx": 85, "dpad_cy": 148,
    "dpad_h": (67, 141, 36, 14),       # horizontal bar (x, y, w, h)
    "dpad_v": (78, 130, 14, 36),       # vertical bar
    "a": (248, 105, 12),               # ABXY (cx, cy, radius)
    "b": (268, 85, 12),
    "x": (228, 85, 12),
    "y": (248, 65, 12),
}

STICK_MAX_OFFSET = 14  # max pixel offset for stick dot


class ControllerOverlay(QWidget):
    """Transparent, click-through, always-on-top overlay widget."""

    def __init__(self, gamepad: GamepadManager, theme: Theme, opacity=0.9):
        super().__init__()
        self.gamepad = gamepad
        self.theme = theme
        self.opacity = opacity

        self._setup_window()
        self._start_polling()

    def _setup_window(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(300, 220)

        # Position at bottom-right of primary screen
        screen = self.screen() or QApplication.primaryScreen()
        geo = screen.availableGeometry()
        self.move(geo.right() - 320, geo.bottom() - 240)

    def showEvent(self, event):
        super().showEvent(event)
        # Enable click-through via Win32
        hwnd = int(self.winId())
        user32 = ctypes.windll.user32
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_TRANSPARENT | WS_EX_LAYERED)

    def _start_polling(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._poll)
        self._timer.start(8)  # ~120Hz

    def _poll(self):
        state = self.gamepad.poll()
        self.update()  # trigger repaint

    def set_theme(self, theme: Theme):
        self.theme = theme
        self.update()

    def set_opacity(self, opacity: float):
        self.opacity = opacity
        self.update()

    def paintEvent(self, event):
        state = self.gamepad.state
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setOpacity(self.opacity)

        theme = self.theme

        if not state.connected:
            p.setPen(QColor(theme.outline))
            p.setFont(QFont("Arial", 12))
            p.drawText(self.rect(), Qt.AlignCenter, "未检测到手柄")
            p.end()
            return

        # --- Controller body ---
        body = LAYOUT["body"]
        p.setPen(QPen(QColor(theme.outline), 2))
        p.setBrush(QColor(theme.body_fill))
        p.drawRoundedRect(body[0], body[1], body[2], body[3], 20, 20)

        # --- Triggers LT/RT ---
        for trig in ("lt", "rt"):
            r = LAYOUT[trig]
            color = theme.highlight[trig] if state.buttons.get(trig, False) or state.axes.get(trig, 0) > 0.1 else theme.btn_default
            # For triggers, check axis value instead of button
            if trig == "lt":
                active = state.axes.get("lt", 0) > 0.1
            else:
                active = state.axes.get("rt", 0) > 0.1
            color = theme.highlight[trig] if active else theme.btn_default
            p.setPen(QPen(QColor(theme.outline), 1))
            p.setBrush(QColor(color))
            p.drawRoundedRect(r[0], r[1], r[2], r[3], 6, 6)

        # --- Bumpers LB/RB ---
        for bmp in ("lb", "rb"):
            r = LAYOUT[bmp]
            active = state.buttons.get(bmp, False)
            color = theme.highlight[bmp] if active else theme.btn_default
            p.setPen(QPen(QColor(theme.outline), 1))
            p.setBrush(QColor(color))
            p.drawRoundedRect(r[0], r[1], r[2], r[3], 4, 4)

        # --- Guide button ---
        gcx, gcy, gr = LAYOUT["guide"]
        active = state.buttons.get("guide", False)
        color = theme.highlight["guide"] if active else theme.btn_default
        p.setPen(QPen(QColor(theme.outline), 1.5))
        p.setBrush(QColor(color))
        p.drawEllipse(gcx - gr, gcy - gr, gr * 2, gr * 2)

        # --- Back / Start ---
        for btn_name, key in (("back", "back"), ("start", "start")):
            cx, cy, r = LAYOUT[btn_name]
            active = state.buttons.get(key, False)
            color = theme.highlight[key] if active else theme.btn_default
            p.setPen(QPen(QColor(theme.outline), 1))
            p.setBrush(QColor(color))
            p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # --- Left stick ---
        lcx, lcy, lr = LAYOUT["ls"]
        p.setPen(QPen(QColor(theme.outline), 1.5))
        p.setBrush(QColor(theme.btn_default))
        p.drawEllipse(lcx - lr, lcy - lr, lr * 2, lr * 2)

        ls_ox = state.axes.get("ls_x", 0) * STICK_MAX_OFFSET
        ls_oy = state.axes.get("ls_y", 0) * STICK_MAX_OFFSET
        ldx, ldy, ldr = LAYOUT["ls_dot"]
        ls_active = abs(ls_ox) > 0.5 or abs(ls_oy) > 0.5
        color = theme.highlight["ls"] if ls_active else theme.highlight.get("ls", theme.outline)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(color))
        p.drawEllipse(ldx + ls_ox - ldr, ldy + ls_oy - ldr, ldr * 2, ldr * 2)

        # --- Right stick ---
        rcx, rcy, rr = LAYOUT["rs"]
        p.setPen(QPen(QColor(theme.outline), 1.5))
        p.setBrush(QColor(theme.btn_default))
        p.drawEllipse(rcx - rr, rcy - rr, rr * 2, rr * 2)

        rs_ox = state.axes.get("rs_x", 0) * STICK_MAX_OFFSET
        rs_oy = state.axes.get("rs_y", 0) * STICK_MAX_OFFSET
        rdx, rdy, rdr = LAYOUT["rs_dot"]
        rs_active = abs(rs_ox) > 0.5 or abs(rs_oy) > 0.5
        color = theme.highlight["rs"] if rs_active else theme.highlight.get("rs", theme.outline)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(color))
        p.drawEllipse(rdx + rs_ox - rdr, rdy + rs_oy - rdr, rdr * 2, rdr * 2)

        # --- D-pad ---
        dhx, dhy, dhw, dhh = LAYOUT["dpad_h"]
        dvx, dvy, dvw, dvh = LAYOUT["dpad_v"]
        dpad_x, dpad_y = state.hats.get("dpad", (0, 0))

        # Horizontal bar
        h_active = dpad_x != 0
        color = theme.highlight["dpad"] if h_active else theme.btn_default
        p.setPen(QPen(QColor(theme.outline), 1))
        p.setBrush(QColor(color))
        p.drawRoundedRect(dhx, dhy, dhw, dhh, 3, 3)

        # Vertical bar
        v_active = dpad_y != 0
        color = theme.highlight["dpad"] if v_active else theme.btn_default
        p.setPen(QPen(QColor(theme.outline), 1))
        p.setBrush(QColor(color))
        p.drawRoundedRect(dvx, dvy, dvw, dvh, 3, 3)

        # --- ABXY buttons ---
        labels = {"a": "A", "b": "B", "x": "X", "y": "Y"}
        p.setFont(QFont("Arial", 9, QFont.Bold))
        for btn_name in ("a", "b", "x", "y"):
            cx, cy, r = LAYOUT[btn_name]
            active = state.buttons.get(btn_name, False)
            color = theme.highlight[btn_name] if active else theme.btn_default
            p.setPen(QPen(QColor(theme.outline), 1.5))
            p.setBrush(QColor(color))
            p.drawEllipse(cx - r, cy - r, r * 2, r * 2)
            # Draw label
            text_color = theme.body_fill if active else theme.outline
            p.setPen(QColor(text_color))
            p.drawText(cx - 6, cy + 4, labels[btn_name])

        p.end()
```

- [ ] **Step 2: Manual smoke test — import check**

Run: `python -c "from overlay import ControllerOverlay; print('OK')"`
Expected: `OK` (import succeeds, no runtime errors from class definition)

- [ ] **Step 3: Commit**

```bash
git add overlay.py
git commit -m "feat: add transparent overlay with QPainter controller rendering"
```

---

### Task 5: System Tray Icon

**Files:**
- Create: `tray.py`

- [ ] **Step 1: Write tray.py**

```python
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QActionGroup
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import QObject, pyqtSignal

from themes import THEMES, Theme


def create_tray_icon():
    """Create a simple gamepad icon for the system tray."""
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(0, 0, 0, 0))
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.Antialiasing)
    # Simple controller silhouette
    p.setBrush(QColor("#4A9EFF"))
    p.setPen(QPen(QColor("#5AB8FF"), 2))
    p.drawRoundedRect(8, 18, 48, 28, 10, 10)
    # Two grips
    p.drawRoundedRect(4, 30, 18, 22, 6, 6)
    p.drawRoundedRect(42, 30, 18, 22, 6, 6)
    # Dpad dot
    p.setBrush(QColor("#FFF"))
    p.setPen(Qt.NoPen)
    p.drawEllipse(20, 28, 6, 6)
    # Buttons dot
    p.drawEllipse(38, 26, 5, 5)
    p.drawEllipse(44, 32, 5, 5)
    p.end()
    return QIcon(pixmap)


class TrayController(QObject):
    """System tray icon with context menu for settings."""

    theme_changed = pyqtSignal(str)    # emits theme name
    opacity_changed = pyqtSignal(float)  # emits opacity 0.5-1.0
    quit_requested = pyqtSignal()

    def __init__(self, get_controller_name=None):
        super().__init__()
        self._get_controller_name = get_controller_name or (lambda: "未连接")
        self._tray = QSystemTrayIcon(create_tray_icon())
        self._menu = QMenu()
        self._build_menu()
        self._tray.setContextMenu(self._menu)
        self._tray.setToolTip("手柄投影 - 未连接")
        self._tray.show()

    def _build_menu(self):
        self._menu.clear()

        # Status line (non-clickable)
        status = QAction(f"手柄: {self._get_controller_name()}", self._menu)
        status.setEnabled(False)
        self._menu.addAction(status)
        self._menu.addSeparator()

        # Opacity submenu
        opacity_menu = self._menu.addMenu("透明度")
        opacity_group = QActionGroup(self)
        for label, value in [("100%", 0.9), ("80%", 0.72), ("60%", 0.54)]:
            act = opacity_menu.addAction(label)
            act.setData(value)
            act.setCheckable(True)
            act.setActionGroup(opacity_group)
            if value == 0.9:
                act.setChecked(True)
            act.triggered.connect(lambda checked, v=value: self.opacity_changed.emit(v))

        # Theme submenu
        theme_menu = self._menu.addMenu("配色主题")
        theme_group = QActionGroup(self)
        for name in THEMES:
            act = theme_menu.addAction(name)
            act.setData(name)
            act.setCheckable(True)
            act.setActionGroup(theme_group)
            if name == "white":
                act.setChecked(True)
            act.triggered.connect(lambda checked, n=name: self.theme_changed.emit(n))

        self._menu.addSeparator()

        # Quit
        quit_act = self._menu.addAction("退出")
        quit_act.triggered.connect(self.quit_requested.emit)

    def update_status(self):
        """Refresh tray tooltip and menu status line."""
        name = self._get_controller_name()
        connected = name != "未连接" and name != ""
        tooltip = f"手柄投影 - {name}" if connected else "手柄投影 - 未连接"
        self._tray.setToolTip(tooltip)
        # Rebuild menu to update status line
        self._build_menu()
```

Note: The import `from PyQt5.QtCore import Qt` is needed for `Qt.NoPen`. Add it to the imports at the top of the file.

- [ ] **Step 2: Add the missing import**

The import line at the top of `tray.py` should include `Qt`:

```python
from PyQt5.QtCore import QObject, pyqtSignal, Qt
```

- [ ] **Step 3: Manual smoke test — import check**

Run: `python -c "from tray import TrayController, create_tray_icon; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add tray.py
git commit -m "feat: add system tray icon with opacity/theme menus"
```

---

### Task 6: Entry Point Integration

**Files:**
- Create: `main.py`

This ties all modules together into a runnable application.

- [ ] **Step 1: Write main.py**

```python
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from gamepad import GamepadManager
from overlay import ControllerOverlay
from tray import TrayController
from themes import THEMES


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # keep running in tray

    # Init gamepad
    gamepad = GamepadManager()
    if not gamepad.init_sdl():
        print("Failed to initialize SDL2")
        sys.exit(1)

    # Create overlay with default theme
    overlay = ControllerOverlay(gamepad, THEMES["white"], opacity=0.9)
    overlay.show()

    # Create tray
    def get_name():
        if gamepad.state.connected:
            return gamepad.state.name
        return "未连接"

    tray = TrayController(get_controller_name=get_name)

    # Connect tray signals
    def on_theme_changed(name):
        overlay.set_theme(THEMES[name])

    def on_opacity_changed(value):
        overlay.set_opacity(value)

    def on_quit():
        gamepad.close()
        app.quit()

    tray.theme_changed.connect(on_theme_changed)
    tray.opacity_changed.connect(on_opacity_changed)
    tray.quit_requested.connect(on_quit)

    # Periodically update tray status (every 2s)
    status_timer = QTimer()
    status_timer.timeout.connect(tray.update_status)
    status_timer.start(2000)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the app**

Run: `python main.py`
Expected:
- Tray icon appears in Windows taskbar with gamepad icon
- Transparent overlay appears at bottom-right of screen
- Right-click tray shows menu with 透明度/配色主题/退出
- If gamepad connected: button presses highlight overlay buttons in real-time
- If no gamepad: overlay shows "未检测到手柄"
- Mouse clicks pass through the overlay to windows beneath

Test manually:
1. Plug in an Xbox controller → overlay should start showing feedback
2. Press A/B/X/Y → corresponding button highlights on overlay
3. Move left stick → dot on overlay moves accordingly
4. Right-click tray → 透明度 → switch to 60% → overlay becomes more transparent
5. Right-click tray → 配色主题 → 黑色 → overlay switches to dark theme
6. Right-click tray → 退出 → app closes cleanly

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add main entry point integrating all modules"
```

---

### Task 7: Visual Polish and Bug Fixes

**Files:**
- Modify: `overlay.py`
- Modify: `tray.py`

After manual testing, fix any issues found.

- [ ] **Step 1: Test with a real gamepad and note issues**

Run the app and test all inputs:
- ABXY buttons
- LB/RB bumpers
- LT/RT triggers (verify axis-based detection works)
- Left/right sticks (verify smooth movement, no jitter in deadzone)
- D-pad all 4 directions + diagonals
- Start/Back/Guide buttons
- Disconnect gamepad mid-use → verify "未检测到手柄" appears
- Reconnect gamepad → verify overlay resumes automatically

- [ ] **Step 2: Fix any rendering issues**

Common adjustments that may be needed:
- Button label text alignment (adjust `cx - N, cy + N` offsets if labels look off-center)
- Stick dot offset scaling (adjust `STICK_MAX_OFFSET` if movement range feels wrong)
- Theme colors (adjust hex values if contrast is insufficient)
- Body rounded rect corner radius (adjust if shape looks wrong)

- [ ] **Step 3: Add Chinese labels to ABXY buttons (optional, adjust per preference)**

If the letters A/B/X/Y look misaligned, adjust the drawText offsets. The current values `cx - 6, cy + 4` may need tuning based on actual font metrics.

- [ ] **Step 4: Commit fixes**

```bash
git add -u
git commit -m "fix: visual polish adjustments from manual testing"
```

---

### Task 8: PyInstaller Packaging

**Files:**
- Create: `controller_overlay.spec` (auto-generated, then customized)

- [ ] **Step 1: Create a minimal app icon (optional)**

If you want a custom icon for the exe, create `gamepad.ico` (16x16, 32x32, 48x48). Otherwise skip the `--icon` flag.

- [ ] **Step 2: Build single-file exe**

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "ControllerOverlay" main.py
```

If you have an icon file:
```bash
pyinstaller --onefile --noconsole --icon=gamepad.ico --name "ControllerOverlay" main.py
```

Expected: `dist/ControllerOverlay.exe` created, ~15-25MB

- [ ] **Step 3: Test the packaged exe**

Run: `dist\ControllerOverlay.exe`
Expected: Same behavior as `python main.py` — tray icon, overlay, all features work

- [ ] **Step 4: Verify portability**

Copy `dist\ControllerOverlay.exe` to a different directory (no other files). Run it.
Expected: Works standalone, no missing DLLs, no console window.

- [ ] **Step 5: Commit packaging config**

```bash
git add -u
git commit -m "build: add PyInstaller packaging configuration"
```
