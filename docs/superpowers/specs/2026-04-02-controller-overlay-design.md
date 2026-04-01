# Game Controller Screen Overlay Plugin - Design Spec

## Summary

A lightweight Windows desktop overlay that displays a real-time game controller visualization. The overlay is always-on-top, click-through, and transparent — showing button presses and joystick movements as visual feedback. Inspired by Snipaste/Translucent's minimal UX: no visible windows or menus, all interaction via system tray icon.

## Architecture

**Approach**: Single-thread QTimer polling (Python + PySDL2 + PyQt5)

```
System Tray Icon (right-click menu: opacity, theme, exit)
       │
Transparent Overlay Window (always-on-top, click-through)
       │
QTimer (8ms / ~120Hz) → PySDL2 Joystick Poll → UI State Update → QPainter redraw
```

All logic runs on the PyQt5 main thread. QTimer calls SDL2 polling at ~120Hz; results directly update the overlay painting. No cross-thread communication, no locks.

## User Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| UI rendering | SVG + code (mixed) | SVG for controller body outline, code controls button color/highlight state. Lightweight, themeable, no external image files. |
| Controller support | Xbox UI + multi-pad compat (SDL2) | SDL2 reads all gamepads, UI always shows Xbox layout. PS/Switch buttons auto-mapped. |
| V1 features | Transparency + color themes | Deadzone and auto-start deferred to future versions. |
| Window interaction | Pure click-through + tray menu | Overlay always penetrates mouse clicks. All settings via tray right-click menu. No visible UI chrome. |

## Modules

| File | Responsibility | Dependencies |
|------|---------------|--------------|
| `main.py` | Entry point. Init SDL2 + PyQt5, create tray + overlay. | PySDL2, PyQt5 |
| `gamepad.py` | SDL2 joystick detection, polling, button/axis state. | PySDL2 |
| `overlay.py` | Transparent topmost window. QPainter SVG controller rendering, button highlight, joystick offset. | PyQt5 |
| `tray.py` | System tray icon, context menu (opacity slider, theme picker, exit). | PyQt5 |
| `themes.py` | Color theme definitions (white/black/neon). Per-button color mapping. | None |

## Gamepad Input Mapping

| SDL2 Read | Overlay Visual |
|-----------|---------------|
| `SDL_JoystickGetButton` (0-9) | ABXY / LB / RB / Start / Back / Guide highlight |
| `SDL_JoystickGetAxis` (0-3) | Left/right stick X/Y offset (stick dot displacement) |
| `SDL_JoystickGetHat` (0) | D-pad direction highlight |
| `SDL_JoystickGetAxis` (4-5) | LT/RT trigger press highlight |

Stick axis values (-32768 ~ 32767) normalized to pixel offset within stick draw radius. Built-in deadzone: 5% of axis range.

### Button Index Mapping (Xbox via SDL2)

```
Button 0 → A    Button 1 → B    Button 2 → X    Button 3 → Y
Button 4 → LB   Button 5 → RB
Button 6 → Back  Button 7 → Start  Button 8 → Guide
Axis 0  → Left Stick X    Axis 1  → Left Stick Y
Axis 2  → Right Stick X   Axis 3  → Right Stick Y
Axis 4  → LT              Axis 5  → RT
Hat 0   → D-pad
```

## Overlay Window Properties

```python
Qt.FramelessWindowHint     # No window frame
Qt.WindowStaysOnTopHint    # Always on top
Qt.Tool                    # No taskbar entry
WA_TranslucentBackground   # Transparent background
# Click-through via Win32:
SetWindowLong(hwnd, GWL_EXSTYLE, WS_EX_TRANSPARENT | WS_EX_LAYERED)
```

- Default size: 300x220px
- Default position: bottom-right corner (20px margin from screen edge)
- Background: fully transparent except the controller SVG

## Color Themes

| Theme | Body Fill | Button Default | Button Highlight | Outline |
|-------|-----------|---------------|-----------------|---------|
| White | #E8E8E8 | #CCCCCC | A=#2ECC71 B=#E74C3C X=#3498FF Y=#F1C40F | #999 |
| Black | #2A2A2A | #555555 | A=#3DFF8F B=#FF4D6A X=#5CB8FF Y=#FFE04D | #666 |
| Neon  | #1A1A2E | #333366 | A=#00FFAA B=#FF0066 X=#00AAFF Y=#FFD700 | #4A4AFF |

Inactive elements use the "Button Default" color. When pressed, the corresponding button fills with its "Button Highlight" color.

## Tray Menu Structure

```
🎮 手柄: [Controller Name or "未连接"]
────────────────────────
透明度 ▸  [100%] [80%] [60%]
配色主题 ▸ [白色] [黑色] [霓虹]
────────────────────────
退出
```

- Top line shows detected controller name, or "未检测到手柄" if none.
- Transparency options change overlay opacity (applied to the whole widget).
- Theme changes apply immediately.
- "退出" closes the app cleanly (SDL2 quit + QApplication exit).

## Error Handling

| Scenario | Behavior |
|----------|----------|
| No gamepad at startup | Overlay shows semi-transparent "未检测到手柄" text. Tray tooltip updates. |
| Gamepad disconnects mid-use | Same as above. SDL2 `SDL_JOYDEVICEREMOVED` event triggers. |
| Gamepad reconnects | SDL2 `SDL_JOYDEVICEADDED` auto-detects. Overlay resumes. No restart needed. |
| Multiple gamepads | Default shows first connected. Tray submenu to switch (if 2+ detected). |

## Packaging

- **Tool**: PyInstaller
- **Command**: `pyinstaller --onefile --noconsole --icon=gamepad.ico main.py`
- **Expected size**: 15-25MB (PyQt5 is the bulk)
- **Runtime**: No installation, no internet, no third-party software. Double-click to run.

## Non-Goals (Explicitly Excluded)

- OBS Studio integration, virtual camera, streaming
- Recording or broadcasting functionality
- Online features, accounts, or cloud services
- Plugin/extension system
- Auto-start on Windows boot (future version)
- Custom deadzone UI (future version)
