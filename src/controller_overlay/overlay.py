"""overlay.py — Transparent, click-through overlay widget.

Delegates all SVG rendering to SvgRenderer.  Positions the main
controller image + trigger images in the widget, scaled and placed
according to user settings.
"""

import ctypes
import sys

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont

from .gamepad import GamepadManager, ControllerType
from .themes import Theme
from .svg_renderer import SvgRenderer
from .renderers import TRIGGER_OFFSETS

# Win32 click-through
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
        self._pos_x = 90
        self._pos_y = 85
        self._scale = 30
        self._current_type = None

        # Previous state for change detection
        self._prev_buttons = {}
        self._prev_axes = {}

        self.renderer = SvgRenderer()
        self._setup_window()

    # ------------------------------------------------------------------
    # Window setup
    # ------------------------------------------------------------------

    def _setup_window(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._apply_geometry()

    def showEvent(self, event):
        super().showEvent(event)
        hwnd = int(self.winId())
        user32 = ctypes.windll.user32
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE,
                              style | WS_EX_TRANSPARENT | WS_EX_LAYERED)
        self._start_polling()

    def _start_polling(self):
        if not hasattr(self, '_timer'):
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._poll)
            self._timer.start(8)  # ~120 Hz

    # ------------------------------------------------------------------
    # Polling
    # ------------------------------------------------------------------

    def _poll(self):
        try:
            self.gamepad.poll()
        except Exception:
            return
        state = self.gamepad.state

        new_type = state.controller_type if state.connected else None
        if self._current_type != new_type:
            self._current_type = new_type
            self.renderer.set_controller_type(new_type)
            self._prev_buttons.clear()
            self._prev_axes.clear()
            if state.connected:
                self._apply_geometry()
            else:
                self.hide()

        if not state.connected:
            return

        self._sync_state(state)
        self.update()

    def _sync_state(self, state):
        """Push changed gamepad state into SvgRenderer."""
        if not state.connected:
            return

        # --- Buttons: only push changes ---
        for name, pressed in state.buttons.items():
            if self._prev_buttons.get(name) != pressed:
                color = self.theme.highlight.get(name, '#FF4444')
                if pressed:
                    self.renderer.on_button_pressed(name, color)
                else:
                    self.renderer.on_button_released(name)
                self._prev_buttons[name] = pressed

        # --- Triggers: renderer has its own threshold ---
        lt = state.axes.get('lt', 0.0)
        rt = state.axes.get('rt', 0.0)
        # Ensure trigger colors are always available (they are axes, not buttons)
        for axis_name in ('lt', 'rt'):
            if axis_name not in self.renderer._colors:
                self.renderer._colors[axis_name] = self.theme.highlight.get(axis_name, '#FF4444')
        self.renderer.on_trigger_changed(lt, rt)

        # --- Joysticks: renderer has its own threshold ---
        lx = state.axes.get('ls_x', 0.0)
        ly = state.axes.get('ls_y', 0.0)
        rx = state.axes.get('rs_x', 0.0)
        ry = state.axes.get('rs_y', 0.0)
        self.renderer.on_joystick_changed(lx, ly, rx, ry)

    # ------------------------------------------------------------------
    # Public setters (from tray signals)
    # ------------------------------------------------------------------

    def set_theme(self, theme: Theme):
        self.theme = theme
        self._prev_buttons.clear()  # Force re-push with new colors
        # Clear trigger colors so they get refreshed with new theme
        self.renderer._colors.pop('lt', None)
        self.renderer._colors.pop('rt', None)
        self.renderer._dirty = True
        self.update()

    def set_opacity(self, opacity: float):
        self.opacity = opacity
        self.update()

    def set_position(self, pos_x: int, pos_y: int):
        self._pos_x = max(0, min(100, pos_x))
        self._pos_y = max(0, min(100, pos_y))
        self._apply_position()

    def set_scale(self, scale: int):
        self._scale = max(0, min(100, scale))
        self.renderer.resize_widget(scale)
        self._apply_geometry()

    # ------------------------------------------------------------------
    # Geometry
    # ------------------------------------------------------------------

    def _base_aspect(self):
        """Return (w, h) base aspect including trigger space above."""
        ctype = self._current_type or ControllerType.XBOX
        if ctype == ControllerType.DUALSENSE:
            return 128, 152      # 128-wide, 128 main + 24 trigger space
        return 427, 322          # 427-wide, 240 main + 82 trigger space

    def _apply_geometry(self):
        if self._scale <= 0:
            self.hide()
            return
        if not self.isVisible():
            self.show()

        base_w, base_h = self._base_aspect()
        screen = QApplication.primaryScreen()
        if not screen:
            self.setFixedSize(base_w, base_h)
            return
        geo = screen.availableGeometry()
        factor = self._scale / 100.0

        aspect = base_w / base_h
        w = int(geo.width() * factor)
        h = int(w / aspect)
        if h > geo.height():
            h = int(geo.height() * factor)
            w = int(h * aspect)

        self.setFixedSize(max(w, 80), max(h, 64))
        self._apply_position()

    def _apply_position(self):
        screen = QApplication.primaryScreen()
        if not screen:
            return
        geo = screen.availableGeometry()
        x = int((geo.width() - self.width()) * self._pos_x / 100)
        y = int((geo.height() - self.height()) * self._pos_y / 100)
        self.move(geo.x() + x, geo.y() + y)

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------

    def paintEvent(self, event):
        state = self.gamepad.state
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setOpacity(self.opacity)

        if not state.connected:
            p.setPen(QColor("#CCCCCC"))
            p.setFont(QFont("Microsoft YaHei", 14))
            p.drawText(self.rect(), Qt.AlignCenter, "未连接手柄")
            p.end()
            return

        ctype = state.controller_type
        ww, wh = self.width(), self.height()

        # --- Layout: main controller + triggers above ---
        if ctype == ControllerType.DUALSENSE:
            trigger_space = int(wh * 0.10)
            main_h = wh - trigger_space
            main_w = int(main_h * (128.0 / 128.0))  # Square aspect
            if main_w > ww:
                main_w = ww
                main_h = int(main_w / 1.0)
            main_x = (ww - main_w) // 2
            main_y = trigger_space
        else:
            trigger_space = int(wh * 0.255)
            main_h = wh - trigger_space
            main_w = int(main_h * (427.0 / 240.0))
            if main_w > ww:
                main_w = ww
                main_h = int(main_w * (240.0 / 427.0))
            main_x = (ww - main_w) // 2
            main_y = trigger_space

        # --- Render SVGs ---
        pixmaps = self.renderer.render(main_w, main_h)
        if pixmaps is None:
            p.setPen(QColor("#CCCCCC"))
            p.setFont(QFont("Microsoft YaHei", 14))
            p.drawText(self.rect(), Qt.AlignCenter, "未连接手柄")
            p.end()
            return

        # Draw main controller
        main_pm = pixmaps.get('main')
        if main_pm and not main_pm.isNull():
            p.drawPixmap(main_x, main_y, main_pm)

        # Draw triggers positioned above shoulder buttons
        offsets = TRIGGER_OFFSETS.get(ctype, {})
        for side, pm_key in [('left', 'lt'), ('right', 'rt')]:
            trig_pm = pixmaps.get(pm_key)
            if trig_pm is None or trig_pm.isNull():
                continue

            off = offsets.get(side, {})
            cx_frac = off.get('center_x_frac', 0.5)
            gap = off.get('gap_px', 2)
            overlap_frac = off.get('overlap_frac', 0.0)

            trig_cx = main_x + int(cx_frac * main_w)
            tw = trig_pm.width()
            th = trig_pm.height()
            tx = trig_cx - tw // 2
            # overlap_frac: fraction of main_h to push trigger down into the main
            # image, compensating for whitespace between SVG top edge and shoulder
            overlap = int(overlap_frac * main_h)
            ty = main_y - th - gap + overlap

            p.drawPixmap(tx, ty, trig_pm)

        p.end()
