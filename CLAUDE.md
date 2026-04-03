# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ControllerOverlay (手柄投影) — a Windows desktop tool that displays a real-time, transparent, always-on-top overlay showing gamepad input. Supports Xbox and DualSense (PS5) controller layouts, auto-detected via SDL2. All user interaction is via the system tray icon. UI strings are in Chinese (Simplified).

## Commands

```bash
pip install -r requirements.txt    # Install dependencies (PyQt5, PySDL2)
python main.py                     # Run the application
pytest tests/ -v                   # Run all tests
pytest tests/test_themes.py -v     # Run a single test file
pytest tests/test_gamepad.py::test_axis_normalization -v  # Run a single test
pyinstaller ControllerOverlay.spec # Build exe (uses spec file with assets bundling)
```

## Project Structure

```
main.py                              # Entry point (adds src/ to sys.path)
src/controller_overlay/              # Application package
  ├── gamepad.py, overlay.py, svg_renderer.py, renderers.py, themes.py, tray.py
assets/                              # SVG images (controllers, triggers, logos)
tests/                               # pytest suite + standalone test_render.py
ControllerOverlay.spec               # PyInstaller build config
```

Imports from outside the package use `from controller_overlay.xxx import ...`. Inside the package, modules use relative imports (`from .xxx import ...`). Tests import via `conftest.py` which adds `src/` to `sys.path`.

## Architecture

Single-threaded, timer-driven PyQt5 application. No multi-threading or locks.

**Module dependency graph:**
```
main.py → controller_overlay.{gamepad, overlay, tray, themes}
overlay.py → .gamepad, .themes, .svg_renderer, .renderers
svg_renderer.py → .gamepad (ControllerType enum), .renderers
renderers.py → .gamepad (ControllerType enum only)
tray.py → .themes
gamepad.py → (lazy imports sdl2)
themes.py → (standalone, no imports)
```

**Data flow:**
1. `QTimer` at ~120Hz (8ms) in `ControllerOverlay` calls `GamepadManager.poll()` → `GamepadState`
2. `overlay._sync_state()` pushes state changes into `SvgRenderer` via `on_button_pressed/released`, `on_trigger_changed`, `on_joystick_changed`
3. `SvgRenderer.render()` deep-copies SVG XML templates from `assets/`, modifies element attributes (fill, stroke, transform, linearGradient), serializes to bytes, renders via `QSvgRenderer` to `QPixmap`. Only rebuilds when dirty (state changed or analog threshold 0.02 exceeded)
4. `paintEvent` draws the cached main controller pixmap and trigger pixmaps positioned above shoulder buttons using offsets from `renderers.py`
5. Settings changes: `TrayController` emits `pyqtSignal`s → `overlay.set_theme/set_opacity/set_position/set_scale`

**Signal wiring (in `main.py`):** Tray signals connect through closures — e.g. `theme_changed` looks up `THEMES[name]` before calling `overlay.set_theme()`. A `QTimer` also updates tray status text every 2s.
- `TrayController.theme_changed(str)` → closure → `overlay.set_theme(Theme)`
- `TrayController.opacity_changed(float)` → closure → `overlay.set_opacity(float)`
- `TrayController.position_changed(int, int)` → closure → `overlay.set_position(int, int)`
- `TrayController.scale_changed(int)` → closure → `overlay.set_scale(int)`
- `TrayController.quit_requested()` → `gamepad.close()` + `app.quit()`

**Key modules:**
- `gamepad.py` — `GamepadState` / `GamepadManager`: SDL2 GameController lifecycle, state polling with hot-plug detection, 5% deadzone normalization. Falls back to raw `SDL_Joystick` API if GameController mapping unavailable. `ControllerType` enum: `XBOX`, `DUALSENSE`, `UNKNOWN`
- `overlay.py` — `ControllerOverlay(QWidget)`: Frameless, click-through (Win32 `WS_EX_TRANSPARENT`), translucent window. Delegates all SVG rendering to `SvgRenderer`. Handles geometry (position/scale relative to screen) and painting layout (main controller + trigger images above shoulder buttons)
- `svg_renderer.py` — `SvgRenderer`: Core rendering engine. Loads SVG files from `assets/` as `xml.etree.ElementTree` templates (never modified in place). On each render: deep-copies templates, injects dynamic elements (e.g., Xbox left shoulder arc), modifies element attributes for highlights (button fill/stroke, trigger linearGradient fill, joystick translate transform, D-pad quadrant clipPaths), serializes to `QByteArray`, renders via `QSvgRenderer` to `QPixmap`. Uses dirty flag + analog threshold to skip unnecessary rebuilds. Asset paths resolved via `_image_dir()` which walks up from `__file__` to project root then into `assets/`
- `renderers.py` — Pure data module. Maps logical button names to SVG element IDs: `BUTTON_MAPS[ControllerType][button_name] → list of element IDs`. Trigger placement offsets (`TRIGGER_OFFSETS`), joystick element references (`JOYSTICK_MAPS`), stick centers (`STICK_CENTERS`), D-pad geometry. Unknown controller type falls back to Xbox layout
- `themes.py` — `Theme` dataclass with `highlight` dict (button_name → hex color). `THEMES` dict of 3 themes (white/black/neon)
- `tray.py` — `TrayController(QObject)`: System tray with `pyqtSignal`-based menu. `SettingsDialog(QDialog)`: position (x/y 0-100) and scale (0-100) sliders with live preview

**SVG assets (`assets/` directory):**
- `xbox.svg` — Xbox controller (viewBox 0 0 427 240). All elements are stroke-only paths. Key IDs: A, B, X, Y, LB_top (right shoulder), View, Menu, Share, XBOX, D_Pad. Class-based: Left_Stick (2 paths), Right_Stick (2 paths), D_Pad_Line (5 paths). Left shoulder arc is injected at runtime from `_XBOX_LB_SHOULDER_PATH` constant
- `dualsense.svg` — DualSense/PS5 (viewBox 0 0 128 128). All elements are filled shapes. Key IDs: Cross, Circle, Square, Triangle, L1_Top, R1_Top, PS, Mic_Mute, Touchpad, DPad_Up/Down/Left/Right, Left/Right_Stick_Outer/Inner, L2_Seam, R2_Seam, Lightbar
- `left_trigger.svg` / `right_trigger.svg` — Trigger shapes (viewBox 0 0 90 138). Single `<path>` element each, `fill="#222222"`. ID assigned programmatically as `left_trigger_shape` / `right_trigger_shape`

## SVG rendering approach

The rendering engine manipulates SVG XML directly rather than using QPainter overlays:

- **Button highlights:** Set `fill` and `stroke` attributes on target SVG elements. Xbox uses fill-opacity for semi-transparent highlights; DualSense uses solid fill
- **Trigger fill:** Two-layer approach using QPainter (because QSvgRenderer silently ignores SVG clipPath): base layer is the stroke-only outline, fill layer is the fully-colored shape clipped to the bottom `val` fraction via `QPainter.setClipRect`. `_apply_triggers()` sets the fill color; `_render_trigger_pixmap()` composites the layers
- **Joystick displacement:** Applies `translate(dx, dy)` transform to the inner stick element. DualSense also applies `scale(0.5)` to shrink inner circle. Outer ring gets intensity-based fill-opacity
- **D-pad quadrants:** Creates filled copies of the D_Pad path element, each clipped to a half-plane `<clipPath>` rect for directional distinction
- **Xbox shoulder:** LB_top (SVG element) maps to right shoulder (RB). Left shoulder (LB) arc is extracted from Left_Outer_Cognition and injected as a new `<path id="XBOX_LB_SHOULDER">` element at runtime

All SVG namespace handling uses `{http://www.w3.org/2000/svg}` prefix. `ET.register_namespace()` is called to avoid `ns0:` prefixes in output.

## Adding a new controller layout

1. Add the controller SVG image to `assets/`
2. Add a `ControllerType` enum value in `gamepad.py`
3. Add detection logic in `detect_controller_type()` or `_detect_type()`
4. Create button map (`BUTTON_MAP[button_name] = ["SVG_Element_ID", ...]`) and trigger/stick offsets in `renderers.py`
5. Add template loading entry in `svg_renderer.py` `_load_templates()`
6. Add any controller-specific rendering logic in `svg_renderer.py` (new `_apply_*` methods)

## Conventions

- **Commit messages:** Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`, `build:`)
- **Naming:** snake_case functions/variables, PascalCase classes, UPPER_CASE module constants
- **Imports:** stdlib → third-party → local. Package modules use relative imports (`from .xxx`). External callers use `from controller_overlay.xxx`. `sdl2` is lazy-imported inside methods to avoid errors when SDL2 is not installed
- **Testing:** Test files mirror source names (`test_gamepad.py` for `gamepad.py`). Tests cover pure logic only (no GUI or SDL2 hardware required)
- **Platform:** Windows-only (Win32 `ctypes` for click-through window). No cross-platform abstraction
