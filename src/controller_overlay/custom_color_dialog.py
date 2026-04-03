"""Custom color picker dialog for per-button highlight color assignment."""

import os
import re
import sys

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QWidget, QSizePolicy,
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QFont
from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from PyQt5.QtSvg import QSvgRenderer

from .themes import _make_classic_colors
from .translations import (
    t, DEFAULT_LANG, get_font,
    KEY_CUSTOM_COLOR_TITLE, KEY_CUSTOM_COLOR_SELECTED,
    KEY_CUSTOM_COLOR_HEX, KEY_OK, KEY_CANCEL,
)

# ---------------------------------------------------------------------------
# Preset color swatches
# ---------------------------------------------------------------------------
PRESET_COLORS = [
    "#E74C3C", "#FF6B6B", "#FF8C00", "#F1C40F",
    "#2ECC71", "#00FFAA", "#3498FF", "#5CB8FF",
    "#9B59B6", "#FF0066", "#006FCD", "#FFFFFF",
    "#AAAAAA", "#333333", "#FFD700", "#00AAFF",
]

# ---------------------------------------------------------------------------
# Button click regions in Xbox SVG viewBox coordinates (0 0 427 240)
# ---------------------------------------------------------------------------
_BUTTON_REGIONS = {
    "a":          QRectF(288, 71, 30, 30),
    "b":          QRectF(310, 49, 30, 30),
    "x":          QRectF(263, 49, 30, 30),
    "y":          QRectF(288, 27, 30, 30),
    "lb":         QRectF(68, 0, 62, 28),
    "rb":         QRectF(268, 0, 62, 28),
    "back":       QRectF(177, 53, 22, 22),
    "start":      QRectF(229, 53, 22, 22),
    "guide":      QRectF(196, 16, 30, 26),
    "share":      QRectF(202, 74, 26, 18),
    "ls_click":   QRectF(98, 38, 54, 56),
    "rs_click":   QRectF(236, 90, 50, 52),
    "dpad_up":    QRectF(155, 92, 26, 24),
    "dpad_down":  QRectF(155, 126, 26, 24),
    "dpad_left":  QRectF(139, 107, 24, 30),
    "dpad_right": (173, 107, 24, 30),
}

# Fix dpad_right — must be QRectF
_BUTTON_REGIONS["dpad_right"] = QRectF(173, 107, 24, 30)

# Display labels for buttons (for the selected button indicator)
_BUTTON_LABELS = {
    "a": "A", "b": "B", "x": "X", "y": "Y",
    "lb": "LB", "rb": "RB",
    "back": "Back", "start": "Start",
    "guide": "Guide", "share": "Share",
    "ls_click": "L3", "rs_click": "R3",
    "dpad_up": "D-Up", "dpad_down": "D-Down",
    "dpad_left": "D-Left", "dpad_right": "D-Right",
}


def _image_dir():
    """Return the assets directory path."""
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "assets")
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    return os.path.join(project_root, "assets")


class ControllerPreview(QWidget):
    """Displays a controller SVG with clickable button regions."""

    button_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected = None
        self._colors = {}
        self._svg_renderer = None
        self._load_svg()
        self.setMinimumSize(300, 170)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMouseTracking(True)

    def _load_svg(self):
        svg_path = os.path.join(_image_dir(), "xbox.svg")
        if os.path.exists(svg_path):
            self._svg_renderer = QSvgRenderer(svg_path)

    def set_colors(self, colors):
        self._colors = dict(colors)
        self.update()

    def set_selected(self, button_name):
        self._selected = button_name
        self.update()

    def _svg_to_widget(self, rect):
        """Transform a QRectF in SVG viewBox coords to widget coords."""
        if not self._svg_renderer or not self._svg_renderer.isValid():
            return QRectF()
        vb = self._svg_renderer.viewBoxF()
        if vb.isEmpty():
            return QRectF()
        w, h = self.width(), self.height()
        sx = w / vb.width()
        sy = h / vb.height()
        scale = min(sx, sy)
        ox = (w - vb.width() * scale) / 2
        oy = (h - vb.height() * scale) / 2
        return QRectF(
            ox + rect.x() * scale,
            oy + rect.y() * scale,
            rect.width() * scale,
            rect.height() * scale,
        )

    def _widget_to_svg(self, pos):
        """Transform a widget position to SVG viewBox coordinates."""
        if not self._svg_renderer or not self._svg_renderer.isValid():
            return None
        vb = self._svg_renderer.viewBoxF()
        if vb.isEmpty():
            return None
        w, h = self.width(), self.height()
        sx = w / vb.width()
        sy = h / vb.height()
        scale = min(sx, sy)
        ox = (w - vb.width() * scale) / 2
        oy = (h - vb.height() * scale) / 2
        svg_x = (pos.x() - ox) / scale
        svg_y = (pos.y() - oy) / scale
        return svg_x, svg_y

    def _hit_test(self, pos):
        """Return button name at widget position, or None."""
        svg_pos = self._widget_to_svg(pos)
        if svg_pos is None:
            return None
        for name, region in _BUTTON_REGIONS.items():
            if region.contains(svg_pos[0], svg_pos[1]):
                return name
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            name = self._hit_test(event.pos())
            if name:
                self._selected = name
                self.button_clicked.emit(name)
                self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        # Background
        p.fillRect(self.rect(), QColor("#F0F0F0"))
        # Render SVG
        if self._svg_renderer and self._svg_renderer.isValid():
            vb = self._svg_renderer.viewBoxF()
            w, h = self.width(), self.height()
            sx = w / vb.width()
            sy = h / vb.height()
            scale = min(sx, sy)
            ox = (w - vb.width() * scale) / 2
            oy = (h - vb.height() * scale) / 2
            target = QRectF(ox, oy, vb.width() * scale, vb.height() * scale)
            self._svg_renderer.render(p, target)
        # Draw color overlays on buttons
        for name, color_hex in self._colors.items():
            if name in _BUTTON_REGIONS:
                wr = self._svg_to_widget(_BUTTON_REGIONS[name])
                color = QColor(color_hex)
                color.setAlpha(80)
                p.fillRect(wr, color)
        # Draw selection highlight
        if self._selected and self._selected in _BUTTON_REGIONS:
            wr = self._svg_to_widget(_BUTTON_REGIONS[self._selected])
            p.setPen(QPen(QColor("#FF0000"), 2, Qt.DashLine))
            p.setBrush(Qt.NoBrush)
            p.drawRect(wr)
        p.end()


class ColorSwatchButton(QPushButton):
    """A small colored square button for the palette."""

    def __init__(self, color_hex, parent=None):
        super().__init__(parent)
        self._color = color_hex
        self.setFixedSize(28, 28)
        self.setToolTip(color_hex)
        self._update_style()

    def _update_style(self):
        border = "#888888"
        self.setStyleSheet(
            f"background-color: {self._color}; "
            f"border: 1px solid {border}; border-radius: 3px;"
        )

    def color(self):
        return self._color


_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


class CustomColorDialog(QDialog):
    """Dialog for per-button custom color assignment."""

    colors_applied = pyqtSignal(dict)

    def __init__(self, initial_colors=None, lang=DEFAULT_LANG, parent=None):
        super().__init__(parent)
        self._lang = lang
        self._selected_button = None
        self._working_colors = dict(initial_colors or _make_classic_colors())
        self._setup_ui()
        self._apply_language()

    def _setup_ui(self):
        self.setFixedSize(620, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout(self)

        content = QHBoxLayout()

        # --- Left: controller preview ---
        self._preview = ControllerPreview()
        self._preview.set_colors(self._working_colors)
        self._preview.button_clicked.connect(self._on_button_clicked)
        content.addWidget(self._preview, 3)

        # --- Right: color picker ---
        right_panel = QVBoxLayout()

        self._selected_label = QLabel("")
        right_panel.addWidget(self._selected_label)

        # Color swatches grid
        swatch_grid = QGridLayout()
        swatch_grid.setSpacing(4)
        cols = 4
        for i, hex_color in enumerate(PRESET_COLORS):
            btn = ColorSwatchButton(hex_color)
            btn.clicked.connect(lambda checked, c=hex_color: self._on_swatch_clicked(c))
            swatch_grid.addWidget(btn, i // cols, i % cols)
        right_panel.addLayout(swatch_grid)

        # Hex input
        hex_row = QHBoxLayout()
        self._hex_label = QLabel("")
        self._hex_input = QLineEdit()
        self._hex_input.setPlaceholderText("#RRGGBB")
        self._hex_input.setMaxLength(7)
        self._hex_input.returnPressed.connect(self._on_hex_input)
        hex_row.addWidget(self._hex_label)
        hex_row.addWidget(self._hex_input, 1)
        right_panel.addLayout(hex_row)

        # Color preview
        self._color_preview = QLabel()
        self._color_preview.setFixedSize(60, 30)
        self._color_preview.setStyleSheet("border: 1px solid #888; background: transparent;")
        right_panel.addWidget(self._color_preview, alignment=Qt.AlignCenter)

        right_panel.addStretch()
        content.addLayout(right_panel, 2)

        main_layout.addLayout(content)

        # --- Bottom: OK + Cancel ---
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._ok_btn = QPushButton("OK")
        self._ok_btn.clicked.connect(self._on_ok)
        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self._ok_btn)
        btn_row.addWidget(self._cancel_btn)
        main_layout.addLayout(btn_row)

    def _apply_language(self):
        self.setWindowTitle(t(KEY_CUSTOM_COLOR_TITLE, self._lang))
        font_str = get_font(self._lang)
        font = QFont(font_str, 9)
        self.setFont(font)
        self._update_selected_label()
        self._hex_label.setText(t(KEY_CUSTOM_COLOR_HEX, self._lang))
        self._ok_btn.setText(t(KEY_OK, self._lang))
        self._cancel_btn.setText(t(KEY_CANCEL, self._lang))

    def set_language(self, lang):
        self._lang = lang
        self._apply_language()

    def _update_selected_label(self):
        if self._selected_button:
            label = _BUTTON_LABELS.get(self._selected_button, self._selected_button)
            self._selected_label.setText(
                f"{t(KEY_CUSTOM_COLOR_SELECTED, self._lang)} {label}"
            )
            color = self._working_colors.get(self._selected_button, "#FFFFFF")
            self._color_preview.setStyleSheet(
                f"border: 1px solid #888; background-color: {color}; border-radius: 3px;"
            )
            self._hex_input.setText(color)
        else:
            self._selected_label.setText(t(KEY_CUSTOM_COLOR_SELECTED, self._lang))
            self._color_preview.setStyleSheet(
                "border: 1px solid #888; background: transparent; border-radius: 3px;"
            )
            self._hex_input.setText("")

    def _on_button_clicked(self, name):
        self._selected_button = name
        self._preview.set_selected(name)
        self._update_selected_label()

    def _apply_color(self, color_hex):
        if not self._selected_button:
            return
        self._working_colors[self._selected_button] = color_hex
        self._preview.set_colors(self._working_colors)
        self._preview.set_selected(self._selected_button)
        self._update_selected_label()

    def _on_swatch_clicked(self, color_hex):
        self._apply_color(color_hex)

    def _on_hex_input(self):
        text = self._hex_input.text().strip()
        if _HEX_RE.match(text):
            self._apply_color(text)

    def _on_ok(self):
        self.colors_applied.emit(dict(self._working_colors))
        self.accept()
