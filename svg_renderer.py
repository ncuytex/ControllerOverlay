"""svg_renderer.py — SVG element manipulation and rendering engine.

Loads SVG files as XML templates, modifies element attributes
(fill, stroke, transform, clipPath) based on gamepad state,
and renders to QPixmap via QSvgRenderer.

Only rebuilds SVG when gamepad state actually changes.
"""

import os
import re
import sys
import copy
import xml.etree.ElementTree as ET

from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import QByteArray, Qt, QRectF

from gamepad import ControllerType
from renderers import (
    BUTTON_MAPS, TRIGGER_OFFSETS, JOYSTICK_MAPS, STICK_CENTERS,
    XBOX_DPAD_CENTER, XBOX_DPAD_RADIUS,
)

# Register SVG namespaces so ET.tostring() produces clean SVG
ET.register_namespace('', 'http://www.w3.org/2000/svg')
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

_NS = '{http://www.w3.org/2000/svg}'
_XLINK = '{http://www.w3.org/1999/xlink}'

# Minimum analog change to trigger a rebuild
_ANALOG_THRESHOLD = 0.02

# Left shoulder arc extracted from Left_Outer_Cognition in xbox.svg
# (first 2 bezier segments spanning the LB arc)
_XBOX_LB_SHOULDER_PATH = (
    "M157.5,7 "
    "C156.494186,4.175392 154.489044,3.118435 151.502716,2.951471 "
    "C134.602905,2.006618 118.595711,5.154576 106.759605,17.744074"
)


def _image_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# SVG element helpers
# ---------------------------------------------------------------------------

def _find_by_id(root, eid):
    """Return the first element with matching id attribute, or None."""
    for el in root.iter():
        if el.get('id') == eid:
            return el
    return None


def _find_all_by_class(root, cls):
    """Return all elements whose class attribute contains *cls*."""
    result = []
    for el in root.iter():
        if cls in el.get('class', '').split():
            result.append(el)
    return result


def _viewbox(root):
    """Parse viewBox → (x, y, w, h) floats."""
    vb = root.get('viewBox', '')
    parts = vb.replace(',', ' ').split()
    if len(parts) == 4:
        return tuple(float(p) for p in parts)
    # Fallback
    w = float(root.get('width', '100').rstrip('px'))
    h = float(root.get('height', '100').rstrip('px'))
    return (0.0, 0.0, w, h)


def _svg_to_pixmap(root, width, height):
    """Serialize an ET element and render it to a QPixmap."""
    raw = ET.tostring(root, encoding='unicode').encode('utf-8')
    renderer = QSvgRenderer(QByteArray(raw))
    if not renderer.isValid():
        return QPixmap()
    pm = QPixmap(max(width, 1), max(height, 1))
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    renderer.render(p)
    p.end()
    return pm


# ---------------------------------------------------------------------------
# SvgRenderer
# ---------------------------------------------------------------------------

class SvgRenderer:
    """Manages SVG templates and produces QPixmaps reflecting gamepad state."""

    def __init__(self):
        # Original SVG templates (never modified)
        self._templates = {}          # ControllerType → ET root
        self._trigger_templates = {}  # 'left'/'right' → ET root

        # Live state
        self._current_type = None
        self._buttons = {}            # name → bool
        self._colors = {}             # name → hex color
        self._triggers = {'lt': 0.0, 'rt': 0.0}
        self._sticks = {'ls': (0.0, 0.0), 'rs': (0.0, 0.0)}

        # Cache
        self._dirty = True
        self._cache = {}              # 'main'/'lt'/'rt' → QPixmap

        self._load_templates()

    # ------------------------------------------------------------------
    # Template loading
    # ------------------------------------------------------------------

    def _load_templates(self):
        d = _image_dir()
        for ctype, fname in [(ControllerType.XBOX, 'xbox.svg'),
                             (ControllerType.DUALSENSE, 'dualsense.svg')]:
            p = os.path.join(d, fname)
            if os.path.exists(p):
                self._templates[ctype] = ET.parse(p).getroot()

        for side, fname in [('left', 'left_trigger.svg'),
                            ('right', 'right_trigger.svg')]:
            p = os.path.join(d, fname)
            if os.path.exists(p):
                root = ET.parse(p).getroot()
                # Assign an id to the sole <path> for clipPath reference
                for el in root.iter(f'{_NS}path'):
                    if el.get('id') is None:
                        el.set('id', f'{side}_trigger_shape')
                self._trigger_templates[side] = root

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_controller_type(self, ctype):
        if self._current_type != ctype:
            self._current_type = ctype
            self._dirty = True

    def on_button_pressed(self, name, color):
        self._buttons[name] = True
        self._colors[name] = color
        self._dirty = True

    def on_button_released(self, name):
        self._buttons[name] = False
        self._dirty = True

    def on_trigger_changed(self, left, right):
        old_l, old_r = self._triggers['lt'], self._triggers['rt']
        self._triggers['lt'] = left
        self._triggers['rt'] = right
        if abs(left - old_l) > _ANALOG_THRESHOLD or abs(right - old_r) > _ANALOG_THRESHOLD:
            self._dirty = True

    def on_joystick_changed(self, lx, ly, rx, ry):
        old_ls, old_rs = self._sticks['ls'], self._sticks['rs']
        self._sticks['ls'] = (lx, ly)
        self._sticks['rs'] = (rx, ry)
        if (abs(lx - old_ls[0]) > _ANALOG_THRESHOLD or
                abs(ly - old_ls[1]) > _ANALOG_THRESHOLD or
                abs(rx - old_rs[0]) > _ANALOG_THRESHOLD or
                abs(ry - old_rs[1]) > _ANALOG_THRESHOLD):
            self._dirty = True

    def resize_widget(self, scale):
        self._dirty = True

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self, main_w, main_h):
        """Return {'main': QPixmap, 'lt': QPixmap, 'rt': QPixmap}.

        Only rebuilds when state has changed since last call.
        """
        if self._current_type is None or self._current_type not in self._templates:
            return None
        if not self._dirty and self._cache.get('main'):
            return self._cache

        # --- Build working copies from templates ---
        main = copy.deepcopy(self._templates[self._current_type])
        lt = copy.deepcopy(self._trigger_templates.get('left'))
        rt = copy.deepcopy(self._trigger_templates.get('right'))

        # Inject left shoulder arc element for Xbox (extracted from
        # Left_Outer_Cognition) so it can be highlighted independently.
        if self._current_type in (ControllerType.XBOX, ControllerType.UNKNOWN):
            lb = ET.SubElement(main, f'{_NS}path')
            lb.set('id', 'XBOX_LB_SHOULDER')
            lb.set('d', _XBOX_LB_SHOULDER_PATH)
            lb.set('fill', 'none')
            lb.set('stroke', '#000000')
            lb.set('stroke-width', '3')
            lb.set('stroke-linecap', 'round')
            lb.set('stroke-linejoin', 'round')

        # --- Apply modifications ---
        self._apply_buttons(main)
        self._apply_triggers(lt, rt)
        self._apply_joysticks(main)

        # --- Render to pixmaps ---
        self._cache = {}
        self._cache['main'] = _svg_to_pixmap(main, main_w, main_h)

        # Triggers sized proportionally to shoulder width
        offsets = TRIGGER_OFFSETS.get(self._current_type, {})
        lo = offsets.get('left', {})
        trig_w = int(main_w * lo.get('width_frac', 0.12))
        trig_h = int(trig_w * (138.0 / 90.0))   # original aspect ratio
        self._cache['lt'] = _svg_to_pixmap(lt, trig_w, trig_h) if lt else QPixmap()
        self._cache['rt'] = _svg_to_pixmap(rt, trig_w, trig_h) if rt else QPixmap()

        self._dirty = False
        return self._cache

    # ------------------------------------------------------------------
    # Button highlights
    # ------------------------------------------------------------------

    def _apply_buttons(self, root):
        ctype = self._current_type
        bmap = BUTTON_MAPS.get(ctype, {})
        is_xbox = (ctype in (ControllerType.XBOX, ControllerType.UNKNOWN))

        for name, pressed in self._buttons.items():
            if not pressed:
                continue
            color = self._colors.get(name, '#FF0000')
            ids = bmap.get(name, [])
            for eid in ids:
                el = _find_by_id(root, eid)
                if el is None:
                    continue
                if is_xbox:
                    el.set('stroke', color)
                    el.set('fill', color)
                    el.set('fill-opacity', '0.55')
                else:
                    el.set('fill', color)

        # Xbox D-pad special handling
        if is_xbox:
            self._apply_xbox_dpad(root)

        # Xbox stick click via class
        if is_xbox:
            self._apply_xbox_stick_click(root)

    def _apply_xbox_dpad(self, root):
        """Highlight Xbox D-pad quadrants independently using D_Pad path copies."""
        dirs = ['dpad_up', 'dpad_down', 'dpad_left', 'dpad_right']
        active = [d for d in dirs if self._buttons.get(d)]
        if not active:
            return

        color = self._colors.get('dpad_up', '#3498FF')

        # Highlight D_Pad stroke only (no fill on original)
        dpad = _find_by_id(root, 'D_Pad')
        if dpad is not None:
            dpad.set('stroke', color)

        # Highlight cross lines
        for el in _find_all_by_class(root, 'D_Pad_Line'):
            el.set('stroke', color)

        cx, cy = XBOX_DPAD_CENTER
        r = XBOX_DPAD_RADIUS

        # Ensure <defs> exists
        defs = root.find(f'{_NS}defs')
        if defs is None:
            defs = ET.SubElement(root, f'{_NS}defs')
            root.remove(defs)
            root.insert(0, defs)

        for d in active:
            clip_id = f'clip_dpad_{d}'
            for old in defs.findall(f'{_NS}clipPath'):
                if old.get('id') == clip_id:
                    defs.remove(old)

            cp = ET.SubElement(defs, f'{_NS}clipPath')
            cp.set('id', clip_id)
            cliprect = ET.SubElement(cp, f'{_NS}rect')
            if d == 'dpad_up':
                cliprect.set('x', str(cx - r))
                cliprect.set('y', str(cy - r))
                cliprect.set('width', str(r * 2))
                cliprect.set('height', str(r))
            elif d == 'dpad_down':
                cliprect.set('x', str(cx - r))
                cliprect.set('y', str(cy))
                cliprect.set('width', str(r * 2))
                cliprect.set('height', str(r))
            elif d == 'dpad_left':
                cliprect.set('x', str(cx - r))
                cliprect.set('y', str(cy - r))
                cliprect.set('width', str(r))
                cliprect.set('height', str(r * 2))
            elif d == 'dpad_right':
                cliprect.set('x', str(cx))
                cliprect.set('y', str(cy - r))
                cliprect.set('width', str(r))
                cliprect.set('height', str(r * 2))

            # Filled copy of D_Pad path, clipped to quadrant
            if dpad is not None:
                fill_path = copy.deepcopy(dpad)
                if 'id' in fill_path.attrib:
                    del fill_path.attrib['id']
                fill_path.set('fill', color)
                fill_path.set('fill-opacity', '0.45')
                fill_path.set('stroke', 'none')
                fill_path.set('clip-path', f'url(#{clip_id})')
                root.append(fill_path)

    def _apply_xbox_stick_click(self, root):
        """Highlight Xbox stick outlines when clicked."""
        for stick, cls_name in [('ls_click', 'Left_Stick'), ('rs_click', 'Right_Stick')]:
            if not self._buttons.get(stick):
                continue
            color = self._colors.get(stick, '#00AAFF')
            for el in _find_all_by_class(root, cls_name):
                el.set('stroke', color)
                el.set('fill', color)
                el.set('fill-opacity', '0.5')

    # ------------------------------------------------------------------
    # Trigger fill
    # ------------------------------------------------------------------

    def _apply_triggers(self, lt_root, rt_root):
        """Apply progressive trigger fill using linearGradient on path fill."""
        for side, root, axis_name in [('left', lt_root, 'lt'),
                                       ('right', rt_root, 'rt')]:
            if root is None:
                continue
            val = self._triggers[axis_name]
            if val < 0.01:
                continue

            color = self._colors.get(axis_name, '#FF4444')

            shape_el = _find_by_id(root, f'{side}_trigger_shape')
            if shape_el is None:
                continue

            _, _, vb_w, vb_h = _viewbox(root)

            # Add <defs> with linearGradient
            defs = root.find(f'{_NS}defs')
            if defs is None:
                defs = ET.SubElement(root, f'{_NS}defs')
                root.remove(defs)
                root.insert(0, defs)

            # Full fill — set color directly
            if val >= 0.99:
                shape_el.set('fill', color)
                shape_el.set('fill-opacity', '0.7')
                continue

            grad_id = f'{side}_fill_gradient'
            for old in defs.findall(f'{_NS}linearGradient'):
                if old.get('id') == grad_id:
                    defs.remove(old)

            lg = ET.SubElement(defs, f'{_NS}linearGradient')
            lg.set('id', grad_id)
            lg.set('gradientUnits', 'userSpaceOnUse')
            lg.set('x1', '0')
            lg.set('y1', str(vb_h))       # bottom
            lg.set('x2', '0')
            lg.set('y2', '0')             # top

            # Bottom portion: highlight color
            s1 = ET.SubElement(lg, f'{_NS}stop')
            s1.set('offset', '0')
            s1.set('stop-color', color)
            s1.set('stop-opacity', '0.7')

            s2 = ET.SubElement(lg, f'{_NS}stop')
            s2.set('offset', f'{val:.4f}')
            s2.set('stop-color', color)
            s2.set('stop-opacity', '0.7')

            # Upper portion: original fill (#222222)
            s3 = ET.SubElement(lg, f'{_NS}stop')
            s3.set('offset', f'{val:.4f}')
            s3.set('stop-color', '#222222')

            s4 = ET.SubElement(lg, f'{_NS}stop')
            s4.set('offset', '1')
            s4.set('stop-color', '#222222')

            shape_el.set('fill', f'url(#{grad_id})')

    # ------------------------------------------------------------------
    # Joystick displacement & intensity
    # ------------------------------------------------------------------

    def _apply_joysticks(self, root):
        ctype = self._current_type
        is_xbox = (ctype in (ControllerType.XBOX, ControllerType.UNKNOWN))

        for stick, (x, y) in self._sticks.items():
            mag = (x * x + y * y) ** 0.5
            click_name = f'{stick}_click'
            color = self._colors.get(click_name, '#00AAFF')

            if is_xbox:
                self._apply_xbox_joystick(root, stick, x, y, mag, color)
            else:
                self._apply_ds_joystick(root, stick, x, y, mag, color)

    def _apply_xbox_joystick(self, root, stick, x, y, mag, color):
        cls_name = 'Left_Stick' if stick == 'ls' else 'Right_Stick'
        els = _find_all_by_class(root, cls_name)
        if len(els) < 2:
            return

        # Determine inner vs outer by bounding box approximation
        # We compare the first coordinate pair in the 'd' attribute
        def _first_coord(el):
            d = el.get('d', '').strip()
            m = re.match(r'M\s*([\d.]+)[,\s]+([\d.]+)', d)
            return (float(m.group(1)), float(m.group(2))) if m else (0, 0)

        centers = [_first_coord(el) for el in els]
        # The one closer to the known stick center is inner
        centers_map = {'ls': (124, 64), 'rs': (260, 117)}
        sc = centers_map.get(stick, (0, 0))
        dists = [((c[0] - sc[0])**2 + (c[1] - sc[1])**2) for c in centers]

        # Both are close; instead, identify by path complexity
        # The outer ring path tends to be longer. Use 'd' attribute length.
        if len(els[0].get('d', '')) > len(els[1].get('d', '')):
            outer, inner = els[0], els[1]
        else:
            outer, inner = els[1], els[0]

        if mag > 0.02:
            # Outer ring: fill with intensity proportional to magnitude
            outer.set('fill', color)
            outer.set('fill-opacity', f'{min(mag * 0.5, 0.5):.2f}')

            # Inner circle: translate for 360° displacement + fill highlight
            centers = {'ls': (124, 64), 'rs': (260, 117)}
            cx, cy = centers.get(stick, (0, 0))
            dx = x * 5.0
            dy = y * 5.0
            inner.set('transform', f'translate({dx:.2f},{dy:.2f})')
            inner.set('fill', color)
            inner.set('fill-opacity', f'{min(mag, 1.0):.2f}')
            inner.set('stroke', color)
        elif self._buttons.get(f'{stick}_click'):
            # Only clicked, no movement
            for el in els:
                el.set('stroke', color)
                el.set('fill', color)
                el.set('fill-opacity', '0.5')

    def _apply_ds_joystick(self, root, stick, x, y, mag, color):
        jmap = JOYSTICK_MAPS.get(ControllerType.DUALSENSE, {}).get(stick, {})
        outer_id = jmap.get('outer')
        inner_id = jmap.get('inner')
        if not outer_id or not inner_id:
            return

        outer_el = _find_by_id(root, outer_id)
        inner_el = _find_by_id(root, inner_id)
        if outer_el is None or inner_el is None:
            return

        if mag > 0.02:
            # Outer ring fill intensity
            outer_el.set('fill', color)
            outer_el.set('fill-opacity', f'{min(mag * 0.5, 0.5):.2f}')

            # Inner circle displacement + fill
            # DualSense viewBox is 128x128; max displacement ~5 SVG units
            scale = 5.0
            dx = x * scale
            dy = y * scale

            # Shrink inner to 50%: get current center, apply scale transform
            centers = {'ls': (45.5, 64.5), 'rs': (82.5, 64.5)}
            cx, cy = centers.get(stick, (64, 64))

            inner_el.set('transform',
                         f'translate({cx + dx:.2f},{cy + dy:.2f}) scale(0.5) translate({-cx:.2f},{-cy:.2f})')
            inner_el.set('fill', color)
            inner_el.set('fill-opacity', f'{min(mag, 1.0):.2f}')
        elif self._buttons.get(f'{stick}_click'):
            # Just clicked
            outer_el.set('fill', color)
            outer_el.set('fill-opacity', '0.5')
            inner_el.set('fill', color)
