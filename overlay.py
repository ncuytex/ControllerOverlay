import ctypes
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont

from gamepad import GamepadManager
from themes import Theme
from renderers import get_renderer

# Win32 constants for click-through
GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
WS_EX_LAYERED = 0x00080000


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
        self.setFixedSize(500, 400)

        # Position at bottom-right of primary screen
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(geo.right() - 520, geo.bottom() - 420)

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

        if not state.connected:
            p.setPen(QColor(self.theme.outline))
            p.setFont(QFont("Arial", 14))
            p.drawText(self.rect(), Qt.AlignCenter, "未检测到手柄")
            p.end()
            return

        renderer = get_renderer(state.controller_type)
        renderer.render(p, self.theme, state)
        p.end()
