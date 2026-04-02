import os
import re
import sys
import base64
import ctypes
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush, QPixmap
from PyQt5.QtSvg import QSvgRenderer

from gamepad import GamepadManager, ControllerType
from themes import Theme
from renderers import BUTTON_LAYOUTS, STICK_MAX_OFFSET

# Win32 constants for click-through
GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
WS_EX_LAYERED = 0x00080000

_TRIGGER_THRESHOLD = 0.05


def _get_image_dir():
    """Directory containing SVG files (works with PyInstaller too)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


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

        # Cached controller images: ControllerType -> QPixmap
        self._controller_images = {}
        self._current_type = None
        self._load_controller_images()

        self._setup_window()

    # ------------------------------------------------------------------
    # Image loading
    # ------------------------------------------------------------------

    def _load_controller_images(self):
        """Load controller images, render SVGs to cached QPixmaps."""
        img_dir = _get_image_dir()

        for ctype, filename in [
            (ControllerType.XBOX, "xbox.svg"),
            (ControllerType.DUALSENSE, "dualsense.svg"),
        ]:
            path = os.path.join(img_dir, filename)
            if not os.path.exists(path):
                print(f"Warning: Image not found: {path}")
                continue

            # Try rendering via QSvgRenderer first
            pm = self._render_svg(path)
            if pm and not pm.isNull() and self._pixmap_has_content(pm):
                self._controller_images[ctype] = pm
                continue

            # QSvgRenderer failed (e.g. embedded raster in <pattern>)
            # Try extracting embedded PNG from the SVG
            pm = self._extract_png_from_svg(path)
            if pm and not pm.isNull():
                self._controller_images[ctype] = pm
                continue

            print(f"Warning: Could not load image: {path}")

    @staticmethod
    def _render_svg(path):
        """Render an SVG file to a QPixmap via QSvgRenderer."""
        renderer = QSvgRenderer(path)
        if not renderer.isValid():
            return None
        sz = renderer.defaultSize()
        pm = QPixmap(sz)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        renderer.render(p)
        p.end()
        return pm

    @staticmethod
    def _extract_png_from_svg(path):
        """Extract an embedded base64 PNG from an SVG file and load as QPixmap."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            match = re.search(r'xlink:href="data:image/png;base64,([^"]+)"', content)
            if not match:
                return None
            png_data = base64.b64decode(match.group(1))
            pm = QPixmap()
            pm.loadFromData(png_data)
            return pm if not pm.isNull() else None
        except Exception:
            return None

    @staticmethod
    def _pixmap_has_content(pm):
        """Check if a pixmap has any non-transparent pixels."""
        img = pm.toImage()
        w, h = min(img.width(), 200), min(img.height(), 200)
        step_x = max(1, img.width() // w)
        step_y = max(1, img.height() // h)
        for y in range(0, img.height(), step_y):
            for x in range(0, img.width(), step_x):
                if img.pixelColor(x, y).alpha() > 10:
                    return True
        return False

    def _get_image(self, controller_type):
        """Get cached pixmap for controller type, with Xbox as fallback."""
        return (
            self._controller_images.get(controller_type)
            or self._controller_images.get(ControllerType.XBOX)
        )

    def _base_size(self):
        """Get base image dimensions for the current controller."""
        if self.gamepad.state.connected:
            pm = self._get_image(self.gamepad.state.controller_type)
            if pm:
                return pm.width(), pm.height()
        # Fallback: first available image
        for pm in self._controller_images.values():
            return pm.width(), pm.height()
        return 500, 400

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
        self._apply_scale()
        self._apply_position()

    def showEvent(self, event):
        super().showEvent(event)
        # Enable click-through via Win32
        hwnd = int(self.winId())
        user32 = ctypes.windll.user32
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_TRANSPARENT | WS_EX_LAYERED)
        self._start_polling()

    def _start_polling(self):
        if not hasattr(self, '_timer'):
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._poll)
            self._timer.start(8)  # ~120Hz

    # ------------------------------------------------------------------
    # Polling — detect controller type changes for resize
    # ------------------------------------------------------------------

    def _poll(self):
        old_type = self._current_type
        self.gamepad.poll()
        new_type = (
            self.gamepad.state.controller_type
            if self.gamepad.state.connected
            else None
        )
        if old_type != new_type:
            self._current_type = new_type
            self._apply_scale()
            self._apply_position()
        self.update()

    # ------------------------------------------------------------------
    # Public setters
    # ------------------------------------------------------------------

    def set_theme(self, theme: Theme):
        self.theme = theme
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
        self._apply_scale()
        self._apply_position()

    # ------------------------------------------------------------------
    # Scale / position
    # ------------------------------------------------------------------

    def _apply_scale(self):
        if self._scale <= 0:
            self.hide()
            return
        if not self.isVisible():
            self.show()

        base_w, base_h = self._base_size()
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

        img = self._get_image(state.controller_type)
        if img is None:
            p.setPen(QColor("#CCCCCC"))
            p.setFont(QFont("Microsoft YaHei", 14))
            p.drawText(self.rect(), Qt.AlignCenter, "未连接手柄")
            p.end()
            return

        # --- Calculate image → widget mapping (keep aspect ratio, center) ---
        img_w, img_h = img.width(), img.height()
        ww, wh = self.width(), self.height()

        aspect = img_w / img_h
        if ww / wh > aspect:
            draw_h = wh
            draw_w = int(draw_h * aspect)
        else:
            draw_w = ww
            draw_h = int(draw_w / aspect)
        ox = (ww - draw_w) // 2
        oy = (wh - draw_h) // 2

        # --- 1. Draw cached controller image ---
        p.drawPixmap(ox, oy, draw_w, draw_h, img)

        # Scale factors: source coordinates → widget pixels
        sx = draw_w / img_w
        sy = draw_h / img_h

        # --- 2. Draw button highlights ---
        buttons, sticks = BUTTON_LAYOUTS.get(
            state.controller_type,
            BUTTON_LAYOUTS[ControllerType.UNKNOWN],
        )

        for name, (bx, by, bw, bh, shape) in buttons.items():
            # Determine if pressed
            if name in ("lt", "rt"):
                pressed = state.axes.get(name, 0.0) > _TRIGGER_THRESHOLD
            else:
                pressed = state.buttons.get(name, False)
            if not pressed:
                continue

            color = QColor(self.theme.highlight.get(name, "#00FF88"))
            color.setAlpha(130)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(color))

            rx = ox + bx * sx
            ry = oy + by * sy
            rw = bw * sx
            rh = bh * sy

            if shape == "ellipse":
                p.drawEllipse(QRectF(rx, ry, rw, rh))
            else:
                rad = min(rw, rh) * 0.3
                p.drawRoundedRect(QRectF(rx, ry, rw, rh), rad, rad)

        # --- 3. Draw stick movement highlights ---
        for stick_name, (cx, cy, diameter) in sticks.items():
            ax = state.axes.get(f"{stick_name}_x", 0.0)
            ay = state.axes.get(f"{stick_name}_y", 0.0)

            # Always highlight base when stick is clicked
            if state.buttons.get(f"{stick_name}_click", False):
                color = QColor(self.theme.highlight.get(f"{stick_name}_click", "#00FF88"))
                color.setAlpha(130)
                p.setPen(Qt.NoPen)
                p.setBrush(QBrush(color))
                r = diameter / 2
                p.drawEllipse(QRectF(
                    ox + (cx - r) * sx,
                    oy + (cy - r) * sy,
                    diameter * sx,
                    diameter * sy,
                ))

            # Movement dot (when stick is tilted)
            if abs(ax) > 0.02 or abs(ay) > 0.02:
                dot_cx = cx + int(ax * STICK_MAX_OFFSET)
                dot_cy = cy + int(ay * STICK_MAX_OFFSET)
                dot_r = diameter * 0.35  # smaller than full area
                color = QColor(self.theme.highlight.get(f"{stick_name}_click", "#00FF88"))
                color.setAlpha(100)
                p.setPen(Qt.NoPen)
                p.setBrush(QBrush(color))
                p.drawEllipse(QRectF(
                    ox + (dot_cx - dot_r) * sx,
                    oy + (dot_cy - dot_r) * sy,
                    dot_r * 2 * sx,
                    dot_r * 2 * sy,
                ))

        p.end()
