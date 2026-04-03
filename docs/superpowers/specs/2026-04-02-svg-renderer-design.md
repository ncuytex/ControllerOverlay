# SVG Renderer Module Design

## Overview

Replace the current QPainter overlay rendering with direct SVG element manipulation.
Load SVGs as XML, modify element attributes (fill, stroke, clipPath, transform) based on
gamepad state, render via QSvgRenderer to QPixmap, and composite in the overlay widget.

## Architecture

### Files

| File | Action | Purpose |
|------|--------|---------|
| `svg_renderer.py` | NEW | SVG element manipulation + rendering engine |
| `overlay.py` | REWRITE | Overlay widget, delegates rendering to svg_renderer |
| `renderers.py` | REWRITE | SVG element ID mappings + trigger positioning |
| `themes.py` | KEEP | Per-button highlight colors |
| `gamepad.py` | KEEP | GamepadState, GamepadManager |
| `tray.py` | KEEP | System tray, settings |
| `main.py` | MINOR | Update signal wiring |

### Data flow

```
QTimer (8ms)
  → GamepadManager.poll() → GamepadState
  → ControllerOverlay._poll()
    → Map GamepadState to SvgRenderer calls:
      - on_button_pressed/released for each changed button
      - on_trigger_changed(left_value, right_value)
      - on_joystick_changed(lx, ly, rx, ry)
    → SvgRenderer.render() → {main, lt, rt} QPixmaps
    → QPainter draws 3 pixmaps (main + 2 triggers)
```

### SVG Manipulation Strategy

1. At startup: load SVG files as `xml.etree.ElementTree` templates
2. Each frame (if state changed):
   a. Deep-copy templates
   b. Modify element attributes based on current state
   c. Serialize to bytes → create QSvgRenderer → render to QPixmap
3. Cache pixmaps between identical states

### Button Highlight

- Find SVG elements by ID (using mapping tables in renderers.py)
- For pressed buttons: set `fill` to highlight color + `fill-opacity="0.7"`
- For released buttons: revert to original fill (`"none"` for Xbox, `"#000000"` for DualSense)
- For composite shapes (D-pad): add `<clipPath>` elements to clip fill to specific quadrant

### Trigger Fill

- Inject `<defs><clipPath>` referencing trigger path into trigger SVG
- Insert filled `<rect>` clipped by trigger path
- Rect `y` and `height` adjusted based on trigger value (0.0=empty, 1.0=full from bottom)

### Joystick Display

- Outer ring: change `fill-opacity` based on offset magnitude (0.0=transparent, 1.0=full color)
- Inner circle: apply `transform="translate(dx, dy)"` based on X/Y axis values
- Inner circle: scale to 50% of outer ring diameter

### Trigger Compositing

- Triggers rendered as separate QPixmaps
- Positioned in paintEvent relative to shoulder buttons in main SVG
- All 3 pixmaps scaled uniformly by the same factor

### Performance

- State-change detection: only rebuild SVG when GamepadState differs from previous
- At idle (no input): rendering is a no-op, cached pixmaps redrawn
- Deep-copy + XML serialize for small SVGs (< 10KB): sub-millisecond

## SVG Element ID Mappings

### Xbox (xbox.svg, viewBox 0 0 427 240)

| Logical name | SVG element IDs |
|-------------|----------------|
| a | A |
| b | B |
| x | X |
| y | Y |
| lb | LB_top |
| rb | (TBD - verify in SVG) |
| back | View |
| start | Menu |
| guide | XBOX |
| dpad_up | D_Pad + D_Pad_Line (clipped to upper quadrant) |
| dpad_down | D_Pad + D_Pad_Line (clipped to lower quadrant) |
| dpad_left | D_Pad + D_Pad_Line (clipped to left quadrant) |
| dpad_right | D_Pad + D_Pad_Line (clipped to right quadrant) |
| ls_click | Left_Stick |
| rs_click | Right_Stick |
| lt | (via trigger SVG + fill) |
| rt | (via trigger SVG + fill) |

### DualSense (dualsense.svg, viewBox 0 0 128 128)

| Logical name | SVG element IDs |
|-------------|----------------|
| a (cross) | Cross |
| b (circle) | Circle |
| x (square) | Square |
| y (triangle) | Triangle |
| lb | L1_Top |
| rb | R1_Top |
| back | (TBD - verify in SVG) |
| start | (TBD - verify in SVG) |
| guide | PS |
| touchpad | Touchpad |
| misc1 | Mic_Mute |
| dpad_up | DPad_Up |
| dpad_down | DPad_Down |
| dpad_left | DPad_Left |
| dpad_right | DPad_Right |
| ls_click | Left_Stick_Outer, Left_Stick_Inner |
| rs_click | Right_Stick_Outer, Right_Stick_Inner |
| lt | (via trigger SVG + fill) |
| rt | (via trigger SVG + fill) |

## API

```python
class SvgRenderer:
    def set_controller_type(self, controller_type: ControllerType)
    def on_button_pressed(self, button_name: str, color: str)
    def on_button_released(self, button_name: str)
    def on_trigger_changed(self, left_value: float, right_value: float)
    def on_joystick_changed(self, lx: float, ly: float, rx: float, ry: float)
    def render(self, scale: float) -> dict  # Returns {'main': QPixmap, 'lt': QPixmap, 'rt': QPixmap}
    def resize_widget(self, scale: int)
```

## Constraints

- No image overlay for highlights (must modify SVG elements directly)
- No hand-drawn outlines (use provided SVGs only)
- Triggers must stay fixed relative to shoulder buttons during scaling
- Analog values must be linear and smooth (no stepping/jumping)
- SVG element IDs matched exactly, not guessed
