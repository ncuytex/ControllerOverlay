import ctypes
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QFont

from gamepad import GamepadManager
from themes import Theme

# Win32 constants for click-through
GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
WS_EX_LAYERED = 0x00080000

# Controller element positions (within 300x220 widget)
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
        screen = QApplication.primaryScreen()
        if screen:
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
        self.gamepad.poll()
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
        for trig_name, axis_name in (("lt", "lt"), ("rt", "rt")):
            r = LAYOUT[trig_name]
            active = state.axes.get(axis_name, 0) > 0.1
            color = theme.highlight[trig_name] if active else theme.btn_default
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
        for btn_name in ("back", "start"):
            cx, cy, r = LAYOUT[btn_name]
            active = state.buttons.get(btn_name, False)
            color = theme.highlight[btn_name] if active else theme.btn_default
            p.setPen(QPen(QColor(theme.outline), 1))
            p.setBrush(QColor(color))
            p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # --- Left stick ---
        lcx, lcy, lr = LAYOUT["ls"]
        p.setPen(QPen(QColor(theme.outline), 1.5))
        p.setBrush(QColor(theme.btn_default))
        p.drawEllipse(lcx - lr, lcy - lr, lr * 2, lr * 2)

        ls_ox = int(state.axes.get("ls_x", 0) * STICK_MAX_OFFSET)
        ls_oy = int(state.axes.get("ls_y", 0) * STICK_MAX_OFFSET)
        ldx, ldy, ldr = LAYOUT["ls_dot"]
        ls_active = abs(ls_ox) > 0 or abs(ls_oy) > 0
        color = theme.highlight["ls"] if ls_active else theme.outline
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(color))
        p.drawEllipse(ldx + ls_ox - ldr, ldy + ls_oy - ldr, ldr * 2, ldr * 2)

        # --- Right stick ---
        rcx, rcy, rr = LAYOUT["rs"]
        p.setPen(QPen(QColor(theme.outline), 1.5))
        p.setBrush(QColor(theme.btn_default))
        p.drawEllipse(rcx - rr, rcy - rr, rr * 2, rr * 2)

        rs_ox = int(state.axes.get("rs_x", 0) * STICK_MAX_OFFSET)
        rs_oy = int(state.axes.get("rs_y", 0) * STICK_MAX_OFFSET)
        rdx, rdy, rdr = LAYOUT["rs_dot"]
        rs_active = abs(rs_ox) > 0 or abs(rs_oy) > 0
        color = theme.highlight["rs"] if rs_active else theme.outline
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(color))
        p.drawEllipse(rdx + rs_ox - rdr, rdy + rs_oy - rdr, rdr * 2, rdr * 2)

        # --- D-pad ---
        dhx, dhy, dhw, dhh = LAYOUT["dpad_h"]
        dvx, dvy, dvw, dvh = LAYOUT["dpad_v"]
        dpad_x, dpad_y = state.hats.get("dpad", (0, 0))

        h_active = dpad_x != 0
        color = theme.highlight["dpad"] if h_active else theme.btn_default
        p.setPen(QPen(QColor(theme.outline), 1))
        p.setBrush(QColor(color))
        p.drawRoundedRect(dhx, dhy, dhw, dhh, 3, 3)

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
            text_color = theme.body_fill if active else theme.outline
            p.setPen(QColor(text_color))
            p.drawText(cx - 5, cy + 4, labels[btn_name])

        p.end()
