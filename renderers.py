from PyQt5.QtGui import (
    QPainter, QColor, QPen, QFont, QBrush,
    QPainterPath, QLinearGradient, QRadialGradient,
)
from PyQt5.QtCore import Qt, QRectF

from gamepad import ControllerType


# ---------------------------------------------------------------------------
# Layout constants – 500×400 canvas
# ---------------------------------------------------------------------------

STICK_MAX_OFFSET = 18

# ---- Xbox layout ----
XBOX = {
    # Body path control points are computed in _build_xbox_body()
    # Face buttons (cx, cy, radius)
    "a": (373, 195, 16), "b": (400, 168, 16),
    "x": (346, 168, 16), "y": (373, 141, 16),
    # Sticks base (cx, cy, radius)
    "ls": (160, 185, 28), "rs": (310, 270, 28),
    # Stick thumb dots (cx, cy, radius)
    "ls_dot": (160, 185, 12), "rs_dot": (310, 270, 12),
    # Bumpers (x, y, w, h, rx)
    "lb": (95, 72, 85, 18, 9), "rb": (320, 72, 85, 18, 9),
    # Triggers (x, y, w, h, rx)
    "lt": (105, 48, 75, 22, 8), "rt": (320, 48, 75, 22, 8),
    # D-pad center
    "dpad_cx": 160, "dpad_cy": 275,
    # D-pad arms (x, y, w, h)
    "dpad_h": (133, 265, 54, 20),
    "dpad_v": (148, 250, 24, 50),
    # Guide, Back, Start (cx, cy, radius)
    "guide": (250, 108, 14),
    "back": (210, 132, 8), "start": (290, 132, 8),
}

# ---- DualSense layout ----
DS = {
    "a": (370, 200, 16), "b": (397, 173, 16),
    "x": (343, 173, 16), "y": (370, 146, 16),
    "ls": (155, 200, 28), "rs": (315, 275, 28),
    "ls_dot": (155, 200, 12), "rs_dot": (315, 275, 12),
    "lb": (90, 72, 80, 18, 9), "rb": (330, 72, 80, 18, 9),
    "lt": (100, 48, 70, 22, 8), "rt": (330, 48, 70, 22, 8),
    "dpad_cx": 155, "dpad_cy": 280,
    "dpad_h": (128, 270, 54, 20),
    "dpad_v": (143, 255, 24, 50),
    # DualSense-specific
    "touchpad": (188, 118, 124, 48),  # (x, y, w, h)
    "guide": (250, 185, 10),          # PS button
    "back": (205, 135, 26, 14),       # Create button (x, y, w, h)
    "start": (270, 135, 26, 14),      # Options button
    "misc1": (250, 230, 8),           # Mic button (cx, cy, r)
    "lightbar": (210, 100, 80, 4),    # (x, y, w, h)
}


# ---------------------------------------------------------------------------
# Precomputed body paths
# ---------------------------------------------------------------------------

def _build_xbox_body():
    """Build a QPainterPath for Xbox controller body (top-down view)."""
    p = QPainterPath()
    # Start at top-left shoulder area
    p.moveTo(100, 80)
    # Top edge left shoulder
    p.cubicTo(120, 68, 160, 60, 200, 58)
    # Top edge center
    p.cubicTo(230, 57, 270, 57, 300, 58)
    # Top edge right shoulder
    p.cubicTo(340, 60, 380, 68, 400, 80)
    # Right shoulder curve down
    p.cubicTo(420, 92, 430, 110, 428, 135)
    # Right grip outer edge
    p.cubicTo(425, 165, 420, 200, 410, 235)
    # Right grip bottom
    p.cubicTo(405, 260, 395, 285, 380, 300)
    p.cubicTo(370, 310, 360, 318, 355, 320)
    # Right grip inner edge going up
    p.cubicTo(345, 310, 335, 295, 330, 275)
    p.cubicTo(320, 245, 310, 225, 300, 215)
    # Inner bottom center
    p.cubicTo(290, 210, 265, 205, 250, 205)
    p.cubicTo(235, 205, 210, 210, 200, 215)
    # Left grip inner edge
    p.cubicTo(190, 225, 180, 245, 170, 275)
    p.cubicTo(165, 295, 155, 310, 145, 320)
    # Left grip bottom
    p.cubicTo(140, 318, 130, 310, 120, 300)
    p.cubicTo(105, 285, 95, 260, 90, 235)
    # Left grip outer edge going up
    p.cubicTo(80, 200, 75, 165, 72, 135)
    # Left shoulder curve
    p.cubicTo(70, 110, 80, 92, 100, 80)
    p.closeSubpath()
    return p


def _build_dualsense_body():
    """Build a QPainterPath for DualSense controller body (top-down view)."""
    p = QPainterPath()
    # Start at top-left
    p.moveTo(95, 85)
    # Top edge
    p.cubicTo(120, 68, 170, 56, 210, 54)
    p.cubicTo(240, 53, 260, 53, 290, 54)
    p.cubicTo(330, 56, 380, 68, 405, 85)
    # Right shoulder down
    p.cubicTo(425, 98, 435, 120, 432, 145)
    # Right side
    p.cubicTo(428, 175, 420, 210, 415, 245)
    # Right grip
    p.cubicTo(412, 268, 405, 290, 395, 310)
    p.cubicTo(388, 325, 378, 335, 370, 338)
    # Right grip inner
    p.cubicTo(360, 330, 350, 315, 345, 295)
    p.cubicTo(338, 268, 328, 245, 318, 230)
    # Center bottom
    p.cubicTo(308, 222, 285, 215, 250, 215)
    p.cubicTo(215, 215, 192, 222, 182, 230)
    # Left grip inner
    p.cubicTo(172, 245, 162, 268, 155, 295)
    p.cubicTo(150, 315, 140, 330, 130, 338)
    # Left grip
    p.cubicTo(122, 335, 112, 325, 105, 310)
    p.cubicTo(95, 290, 88, 268, 85, 245)
    # Left side up
    p.cubicTo(80, 210, 72, 175, 68, 145)
    # Left shoulder curve
    p.cubicTo(65, 120, 75, 98, 95, 85)
    p.closeSubpath()
    return p


_XBOX_BODY = _build_xbox_body()
_DS_BODY = _build_dualsense_body()


# ---------------------------------------------------------------------------
# Renderer base & implementations
# ---------------------------------------------------------------------------

class BaseControllerRenderer:
    """Base class for controller renderers."""

    def render(self, painter, theme, state):
        self.p = painter
        self.theme = theme
        self.state = state
        self._draw_body()
        self._draw_triggers()
        self._draw_bumpers()
        self._draw_dpad()
        self._draw_sticks()
        self._draw_special()
        self._draw_buttons()

    def _body_gradient(self, path):
        """Create a subtle vertical gradient for the controller body."""
        g = QLinearGradient(0, 50, 0, 340)
        fill = QColor(self.theme.body_fill)
        lighter = fill.lighter(115)
        darker = fill.darker(110)
        g.setColorAt(0.0, lighter)
        g.setColorAt(0.5, fill)
        g.setColorAt(1.0, darker)
        return g

    def _highlight(self, name):
        """Get highlight color for an element."""
        return QColor(self.theme.highlight.get(name, self.theme.outline))

    def _active_color(self, name, is_active):
        """Return highlight color if active, otherwise default button color."""
        if is_active:
            return self._highlight(name)
        return QColor(self.theme.btn_default)

    def _draw_outline(self, width=2):
        self.p.setPen(QPen(QColor(self.theme.outline), width))
        self.p.setBrush(Qt.NoBrush)


class XboxRenderer(BaseControllerRenderer):
    """Renders a realistic Xbox-style controller."""

    def _draw_body(self):
        p = self.p
        outline_pen = QPen(QColor(self.theme.outline), 2.5)
        p.setPen(outline_pen)
        p.setBrush(self._body_gradient(_XBOX_BODY))
        p.drawPath(_XBOX_BODY)

    def _draw_triggers(self):
        p = self.p
        for name in ("lt", "rt"):
            x, y, w, h, rx = XBOX[name]
            val = self.state.axes.get(name, 0.0)
            active = val > 0.05
            color = self._active_color(name, active)

            # Draw trigger outline
            p.setPen(QPen(QColor(self.theme.outline), 1.5))
            p.setBrush(QColor(self.theme.btn_default))
            p.drawRoundedRect(x, y, w, h, rx, rx)

            # Fill proportionally when active
            if active:
                fill_h = int(h * min(val, 1.0))
                p.setPen(Qt.NoPen)
                p.setBrush(color)
                p.drawRoundedRect(x, y + h - fill_h, w, fill_h, rx, rx)

    def _draw_bumpers(self):
        p = self.p
        for name in ("lb", "rb"):
            x, y, w, h, rx = XBOX[name]
            active = self.state.buttons.get(name, False)
            color = self._active_color(name, active)

            g = QLinearGradient(x, y, x, y + h)
            g.setColorAt(0.0, color.lighter(110))
            g.setColorAt(1.0, color)
            p.setPen(QPen(QColor(self.theme.outline), 1.5))
            p.setBrush(QBrush(g))
            p.drawRoundedRect(x, y, w, h, rx, rx)

    def _draw_dpad(self):
        p = self.p
        cx, cy = XBOX["dpad_cx"], XBOX["dpad_cy"]
        hx, hy, hw, hh = XBOX["dpad_h"]
        vx, vy, vw, vh = XBOX["dpad_v"]

        # Horizontal bar
        h_active = self.state.buttons.get("dpad_left", False) or self.state.buttons.get("dpad_right", False)
        h_color = self._active_color("dpad", h_active)
        p.setPen(QPen(QColor(self.theme.outline), 1.5))
        p.setBrush(h_color)
        p.drawRoundedRect(hx, hy, hw, hh, 4, 4)

        # Vertical bar
        v_active = self.state.buttons.get("dpad_up", False) or self.state.buttons.get("dpad_down", False)
        v_color = self._active_color("dpad", v_active)
        p.setBrush(v_color)
        p.drawRoundedRect(vx, vy, vw, vh, 4, 4)

        # Center indent
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(self.theme.outline))
        p.drawEllipse(cx - 3, cy - 3, 6, 6)

    def _draw_sticks(self):
        p = self.p
        for stick, dot in (("ls", "ls_dot"), ("rs", "rs_dot")):
            cx, cy, r = XBOX[stick]
            # Recessed well
            well_g = QRadialGradient(cx, cy, r)
            well_g.setColorAt(0.0, QColor(self.theme.body_fill).darker(130))
            well_g.setColorAt(0.8, QColor(self.theme.body_fill).darker(150))
            well_g.setColorAt(1.0, QColor(self.theme.outline))
            p.setPen(QPen(QColor(self.theme.outline), 1.5))
            p.setBrush(QBrush(well_g))
            p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

            # Thumb cap with offset
            ax = self.state.axes.get(f"{stick}_x", 0.0)
            ay = self.state.axes.get(f"{stick}_y", 0.0)
            ox = int(ax * STICK_MAX_OFFSET)
            oy = int(ay * STICK_MAX_OFFSET)
            dcx, dcy, dr = XBOX[dot]
            dx = dcx + ox
            dy = dcy + oy

            stick_active = abs(ox) > 0 or abs(oy) > 0
            thumb_color = self._active_color(stick, stick_active)

            cap_g = QRadialGradient(dx, dy, dr)
            cap_g.setColorAt(0.0, thumb_color.lighter(120))
            cap_g.setColorAt(0.7, thumb_color)
            cap_g.setColorAt(1.0, thumb_color.darker(120))
            p.setPen(QPen(QColor(self.theme.outline), 1))
            p.setBrush(QBrush(cap_g))
            p.drawEllipse(dx - dr, dy - dr, dr * 2, dr * 2)

            # Inner ring on thumb cap
            p.setPen(QPen(QColor(self.theme.outline).lighter(130), 0.5))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(dx - dr + 3, dy - dr + 3, (dr - 3) * 2, (dr - 3) * 2)

    def _draw_buttons(self):
        p = self.p
        labels = {"a": "A", "b": "B", "x": "X", "y": "Y"}
        p.setFont(QFont("Arial", 10, QFont.Bold))

        for name in ("a", "b", "x", "y"):
            cx, cy, r = XBOX[name]
            active = self.state.buttons.get(name, False)
            color = self._active_color(name, active)

            # Button with gradient
            btn_g = QRadialGradient(cx - 2, cy - 2, r)
            btn_g.setColorAt(0.0, color.lighter(130))
            btn_g.setColorAt(0.6, color)
            btn_g.setColorAt(1.0, color.darker(130))
            p.setPen(QPen(QColor(self.theme.outline), 1.5))
            p.setBrush(QBrush(btn_g))
            p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

            # Label
            text_color = self.theme.body_fill if active else QColor(self.theme.outline).lighter(120)
            p.setPen(QColor(text_color))
            p.drawText(QRectF(cx - r, cy - r, r * 2, r * 2), Qt.AlignCenter, labels[name])

    def _draw_special(self):
        p = self.p
        # Guide button (Xbox logo)
        cx, cy, r = XBOX["guide"]
        active = self.state.buttons.get("guide", False)
        color = self._active_color("guide", active)

        # Glow effect when active
        if active:
            p.setPen(Qt.NoPen)
            glow = QColor(color)
            glow.setAlpha(80)
            p.setBrush(glow)
            p.drawEllipse(cx - r - 6, cy - r - 6, (r + 6) * 2, (r + 6) * 2)

        btn_g = QRadialGradient(cx, cy, r)
        btn_g.setColorAt(0.0, color.lighter(130))
        btn_g.setColorAt(1.0, color)
        p.setPen(QPen(QColor(self.theme.outline), 1.5))
        p.setBrush(QBrush(btn_g))
        p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # Xbox "X" symbol
        p.setPen(QPen(QColor(self.theme.body_fill) if active else QColor(self.theme.outline), 2))
        sz = 5
        p.drawLine(cx - sz, cy - sz, cx + sz, cy + sz)
        p.drawLine(cx + sz, cy - sz, cx - sz, cy + sz)

        # Back button
        cx, cy, r = XBOX["back"]
        active = self.state.buttons.get("back", False)
        color = self._active_color("back", active)
        p.setPen(QPen(QColor(self.theme.outline), 1))
        p.setBrush(color)
        p.drawEllipse(cx - r, cy - r, r * 2, r * 2)
        # Two small rectangles (View icon)
        p.setPen(QPen(QColor(self.theme.body_fill) if active else QColor(self.theme.outline), 1.2))
        p.setBrush(Qt.NoBrush)
        p.drawRect(cx - 4, cy - 2, 4, 4)
        p.drawRect(cx - 1, cy - 2, 4, 4)

        # Start button
        cx, cy, r = XBOX["start"]
        active = self.state.buttons.get("start", False)
        color = self._active_color("start", active)
        p.setPen(QPen(QColor(self.theme.outline), 1))
        p.setBrush(color)
        p.drawEllipse(cx - r, cy - r, r * 2, r * 2)
        # Three lines (Menu icon)
        p.setPen(QPen(QColor(self.theme.body_fill) if active else QColor(self.theme.outline), 1.2))
        p.drawLine(cx - 3, cy - 3, cx + 3, cy - 3)
        p.drawLine(cx - 3, cy, cx + 3, cy)
        p.drawLine(cx - 3, cy + 3, cx + 3, cy + 3)


class DualSenseRenderer(BaseControllerRenderer):
    """Renders a realistic DualSense (PlayStation 5) controller."""

    def _draw_body(self):
        p = self.p
        outline_pen = QPen(QColor(self.theme.outline), 2.5)
        p.setPen(outline_pen)
        p.setBrush(self._body_gradient(_DS_BODY))
        p.drawPath(_DS_BODY)

    def _draw_triggers(self):
        p = self.p
        for name in ("lt", "rt"):
            x, y, w, h, rx = DS[name]
            val = self.state.axes.get(name, 0.0)
            active = val > 0.05
            color = self._active_color(name, active)

            p.setPen(QPen(QColor(self.theme.outline), 1.5))
            p.setBrush(QColor(self.theme.btn_default))
            p.drawRoundedRect(x, y, w, h, rx, rx)

            if active:
                fill_h = int(h * min(val, 1.0))
                p.setPen(Qt.NoPen)
                p.setBrush(color)
                p.drawRoundedRect(x, y + h - fill_h, w, fill_h, rx, rx)

    def _draw_bumpers(self):
        p = self.p
        for name in ("lb", "rb"):
            x, y, w, h, rx = DS[name]
            active = self.state.buttons.get(name, False)
            color = self._active_color(name, active)

            g = QLinearGradient(x, y, x, y + h)
            g.setColorAt(0.0, color.lighter(110))
            g.setColorAt(1.0, color)
            p.setPen(QPen(QColor(self.theme.outline), 1.5))
            p.setBrush(QBrush(g))
            p.drawRoundedRect(x, y, w, h, rx, rx)

    def _draw_dpad(self):
        p = self.p
        cx, cy = DS["dpad_cx"], DS["dpad_cy"]
        hx, hy, hw, hh = DS["dpad_h"]
        vx, vy, vw, vh = DS["dpad_v"]

        h_active = self.state.buttons.get("dpad_left", False) or self.state.buttons.get("dpad_right", False)
        h_color = self._active_color("dpad", h_active)
        p.setPen(QPen(QColor(self.theme.outline), 1.5))
        p.setBrush(h_color)
        p.drawRoundedRect(hx, hy, hw, hh, 4, 4)

        v_active = self.state.buttons.get("dpad_up", False) or self.state.buttons.get("dpad_down", False)
        v_color = self._active_color("dpad", v_active)
        p.setBrush(v_color)
        p.drawRoundedRect(vx, vy, vw, vh, 4, 4)

        # Center indent
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(self.theme.outline))
        p.drawEllipse(cx - 3, cy - 3, 6, 6)

    def _draw_sticks(self):
        p = self.p
        for stick, dot in (("ls", "ls_dot"), ("rs", "rs_dot")):
            cx, cy, r = DS[stick]
            well_g = QRadialGradient(cx, cy, r)
            well_g.setColorAt(0.0, QColor(self.theme.body_fill).darker(130))
            well_g.setColorAt(0.8, QColor(self.theme.body_fill).darker(150))
            well_g.setColorAt(1.0, QColor(self.theme.outline))
            p.setPen(QPen(QColor(self.theme.outline), 1.5))
            p.setBrush(QBrush(well_g))
            p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

            ax = self.state.axes.get(f"{stick}_x", 0.0)
            ay = self.state.axes.get(f"{stick}_y", 0.0)
            ox = int(ax * STICK_MAX_OFFSET)
            oy = int(ay * STICK_MAX_OFFSET)
            dcx, dcy, dr = DS[dot]
            dx = dcx + ox
            dy = dcy + oy

            stick_active = abs(ox) > 0 or abs(oy) > 0
            thumb_color = self._active_color(stick, stick_active)

            cap_g = QRadialGradient(dx, dy, dr)
            cap_g.setColorAt(0.0, thumb_color.lighter(120))
            cap_g.setColorAt(0.7, thumb_color)
            cap_g.setColorAt(1.0, thumb_color.darker(120))
            p.setPen(QPen(QColor(self.theme.outline), 1))
            p.setBrush(QBrush(cap_g))
            p.drawEllipse(dx - dr, dy - dr, dr * 2, dr * 2)

            # Concentric ring
            p.setPen(QPen(QColor(self.theme.outline).lighter(130), 0.5))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(dx - dr + 3, dy - dr + 3, (dr - 3) * 2, (dr - 3) * 2)

    def _draw_buttons(self):
        """Draw PlayStation face buttons with symbols (Cross, Circle, Square, Triangle)."""
        p = self.p
        symbols = {
            "a": "cross",
            "b": "circle",
            "x": "square",
            "y": "triangle",
        }

        for name in ("a", "b", "x", "y"):
            cx, cy, r = DS[name]
            active = self.state.buttons.get(name, False)
            color = self._active_color(name, active)

            # Button base
            btn_g = QRadialGradient(cx - 2, cy - 2, r)
            btn_g.setColorAt(0.0, color.lighter(130))
            btn_g.setColorAt(0.6, color)
            btn_g.setColorAt(1.0, color.darker(130))
            p.setPen(QPen(QColor(self.theme.outline), 1.5))
            p.setBrush(QBrush(btn_g))
            p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

            # Draw symbol
            sym_color = QColor(self.theme.body_fill) if active else QColor(self.theme.outline).lighter(120)
            pen = QPen(sym_color, 2.2)
            p.setPen(pen)
            p.setBrush(Qt.NoBrush)

            sym = symbols[name]
            if sym == "cross":
                sz = 5
                p.drawLine(cx - sz, cy - sz, cx + sz, cy + sz)
                p.drawLine(cx + sz, cy - sz, cx - sz, cy + sz)
            elif sym == "circle":
                p.drawEllipse(cx - 6, cy - 6, 12, 12)
            elif sym == "square":
                p.drawRoundedRect(cx - 5, cy - 5, 10, 10, 1, 1)
            elif sym == "triangle":
                path = QPainterPath()
                path.moveTo(cx, cy - 7)
                path.lineTo(cx - 6, cy + 5)
                path.lineTo(cx + 6, cy + 5)
                path.closeSubpath()
                p.drawPath(path)

    def _draw_special(self):
        p = self.p

        # ---- Touchpad ----
        x, y, w, h = DS["touchpad"]
        active = self.state.buttons.get("touchpad", False)
        tp_color = self._active_color("touchpad", active)
        p.setPen(QPen(QColor(self.theme.outline), 1.5))
        p.setBrush(tp_color)
        p.drawRoundedRect(x, y, w, h, 6, 6)
        # Center dividing line
        p.setPen(QPen(QColor(self.theme.outline), 0.5))
        p.drawLine(x + w // 2, y + 4, x + w // 2, y + h - 4)

        # ---- Light bar ----
        x, y, w, h = DS["lightbar"]
        active = self.state.connected
        bar_color = self._highlight("guide")
        if active:
            glow = QColor(bar_color)
            glow.setAlpha(60)
            p.setPen(Qt.NoPen)
            p.setBrush(glow)
            p.drawRoundedRect(x - 2, y - 2, w + 4, h + 4, 3, 3)
        p.setPen(Qt.NoPen)
        p.setBrush(bar_color if active else QColor(self.theme.btn_default))
        p.drawRoundedRect(x, y, w, h, 2, 2)

        # ---- PS button ----
        cx, cy, r = DS["guide"]
        active = self.state.buttons.get("guide", False)
        color = self._active_color("guide", active)
        p.setPen(QPen(QColor(self.theme.outline), 1.2))
        p.setBrush(color)
        p.drawEllipse(cx - r, cy - r, r * 2, r * 2)
        # PS text
        p.setFont(QFont("Arial", 6, QFont.Bold))
        text_color = self.theme.body_fill if active else QColor(self.theme.outline)
        p.setPen(QColor(text_color))
        p.drawText(QRectF(cx - r, cy - r, r * 2, r * 2), Qt.AlignCenter, "PS")

        # ---- Create button (was Share/Back) ----
        x, y, w, h = DS["back"]
        active = self.state.buttons.get("back", False)
        color = self._active_color("back", active)
        p.setPen(QPen(QColor(self.theme.outline), 1))
        p.setBrush(color)
        p.drawRoundedRect(x, y, w, h, 4, 4)
        # Three lines icon
        icon_color = self.theme.body_fill if active else QColor(self.theme.outline)
        p.setPen(QPen(QColor(icon_color), 1.2))
        mid_y = y + h // 2
        p.drawLine(x + 5, mid_y - 2, x + w - 5, mid_y - 2)
        p.drawLine(x + 5, mid_y + 1, x + w - 5, mid_y + 1)

        # ---- Options button (was Start) ----
        x, y, w, h = DS["start"]
        active = self.state.buttons.get("start", False)
        color = self._active_color("start", active)
        p.setPen(QPen(QColor(self.theme.outline), 1))
        p.setBrush(color)
        p.drawRoundedRect(x, y, w, h, 4, 4)
        # Three dots icon
        icon_color = self.theme.body_fill if active else QColor(self.theme.outline)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(icon_color))
        mid_y = y + h // 2
        for dx in (-4, 0, 4):
            p.drawEllipse(x + w // 2 + dx - 1, mid_y - 1, 2, 2)

        # ---- Mic button ----
        cx, cy, r = DS["misc1"]
        active = self.state.buttons.get("misc1", False)
        color = self._active_color("misc1", active)
        p.setPen(QPen(QColor(self.theme.outline), 1))
        p.setBrush(color)
        p.drawEllipse(cx - r, cy - r, r * 2, r * 2)
        # Mic dot
        icon_color = self.theme.body_fill if active else QColor(self.theme.outline)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(icon_color))
        p.drawEllipse(cx - 2, cy - 3, 4, 4)
        p.drawArc(cx - 3, cy - 1, 6, 6, 0 * 16, 180 * 16)


# ---------------------------------------------------------------------------
# Renderer factory
# ---------------------------------------------------------------------------

_RENDERERS = {
    ControllerType.XBOX: XboxRenderer(),
    ControllerType.DUALSENSE: DualSenseRenderer(),
    ControllerType.UNKNOWN: XboxRenderer(),
}


def get_renderer(controller_type):
    """Return the appropriate renderer for the given controller type."""
    return _RENDERERS.get(controller_type, _RENDERERS[ControllerType.UNKNOWN])
