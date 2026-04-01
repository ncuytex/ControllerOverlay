from enum import Enum


DEADZONE_PERCENT = 0.05
AXIS_MAX = 32767


class ControllerType(Enum):
    XBOX = "xbox"
    DUALSENSE = "dualsense"
    UNKNOWN = "unknown"


# These maps use SDL_GameController button/axis constants.
# They are populated lazily on first import of sdl2 to avoid
# requiring sdl2 at module load time.
_GC_BUTTON_MAP = None
_GC_AXIS_MAP = None

# Logical button names exposed by GamepadState
BUTTON_NAMES = [
    "a", "b", "x", "y",
    "back", "guide", "start",
    "ls_click", "rs_click",
    "lb", "rb",
    "dpad_up", "dpad_down", "dpad_left", "dpad_right",
    "misc1", "touchpad",
]

AXIS_NAMES = ["ls_x", "ls_y", "rs_x", "rs_y", "lt", "rt"]


def _init_maps():
    """Lazily initialize SDL_GameController button/axis maps."""
    global _GC_BUTTON_MAP, _GC_AXIS_MAP
    if _GC_BUTTON_MAP is not None:
        return
    import sdl2

    _GC_BUTTON_MAP = {
        "a":         sdl2.SDL_CONTROLLER_BUTTON_A,
        "b":         sdl2.SDL_CONTROLLER_BUTTON_B,
        "x":         sdl2.SDL_CONTROLLER_BUTTON_X,
        "y":         sdl2.SDL_CONTROLLER_BUTTON_Y,
        "back":      sdl2.SDL_CONTROLLER_BUTTON_BACK,
        "guide":     sdl2.SDL_CONTROLLER_BUTTON_GUIDE,
        "start":     sdl2.SDL_CONTROLLER_BUTTON_START,
        "ls_click":  sdl2.SDL_CONTROLLER_BUTTON_LEFTSTICK,
        "rs_click":  sdl2.SDL_CONTROLLER_BUTTON_RIGHTSTICK,
        "lb":        sdl2.SDL_CONTROLLER_BUTTON_LEFTSHOULDER,
        "rb":        sdl2.SDL_CONTROLLER_BUTTON_RIGHTSHOULDER,
        "dpad_up":   sdl2.SDL_CONTROLLER_BUTTON_DPAD_UP,
        "dpad_down": sdl2.SDL_CONTROLLER_BUTTON_DPAD_DOWN,
        "dpad_left": sdl2.SDL_CONTROLLER_BUTTON_DPAD_LEFT,
        "dpad_right":sdl2.SDL_CONTROLLER_BUTTON_DPAD_RIGHT,
    }
    _GC_AXIS_MAP = {
        "ls_x": sdl2.SDL_CONTROLLER_AXIS_LEFTX,
        "ls_y": sdl2.SDL_CONTROLLER_AXIS_LEFTY,
        "rs_x": sdl2.SDL_CONTROLLER_AXIS_RIGHTX,
        "rs_y": sdl2.SDL_CONTROLLER_AXIS_RIGHTY,
        "lt":   sdl2.SDL_CONTROLLER_AXIS_TRIGGERLEFT,
        "rt":   sdl2.SDL_CONTROLLER_AXIS_TRIGGERRIGHT,
    }
    # DualSense-specific buttons (may not exist in older SDL2)
    for name, val in [
        ("misc1",    getattr(sdl2, "SDL_CONTROLLER_BUTTON_MISC1", 15)),
        ("touchpad", getattr(sdl2, "SDL_CONTROLLER_BUTTON_TOUCHPAD", 20)),
    ]:
        if name not in _GC_BUTTON_MAP:
            _GC_BUTTON_MAP[name] = val


def normalize_axis(value):
    """Normalize a raw SDL2 stick axis value to [-1.0, 1.0] with deadzone."""
    threshold = int(AXIS_MAX * DEADZONE_PERCENT)
    if -threshold < value < threshold:
        return 0.0
    if value > threshold:
        return (value - threshold) / (AXIS_MAX - threshold)
    else:
        return (value + threshold) / (AXIS_MAX - threshold)


def normalize_trigger(value):
    """Normalize a raw SDL2 trigger axis [0, 32767] to [0.0, 1.0] with deadzone."""
    threshold = int(AXIS_MAX * DEADZONE_PERCENT)
    if value < threshold:
        return 0.0
    return (value - threshold) / (AXIS_MAX - threshold)


def detect_controller_type(name):
    """Detect controller type from the device name string."""
    lower = name.lower()
    if "dualsense" in lower or "ps5" in lower:
        return ControllerType.DUALSENSE
    if "xbox" in lower or "microsoft" in lower or "x-input" in lower or "xinput" in lower:
        return ControllerType.XBOX
    return ControllerType.XBOX  # default fallback


class GamepadState:
    """Snapshot of all gamepad inputs at a point in time."""

    def __init__(self):
        self.buttons = {name: False for name in BUTTON_NAMES}
        self.axes = {name: 0.0 for name in AXIS_NAMES}
        self.connected = False
        self.name = ""
        self.controller_type = ControllerType.UNKNOWN


class GamepadManager:
    """Manages SDL2 game controller detection and state polling."""

    def __init__(self):
        self._controller = None
        self._device_index = -1
        self._use_fallback = False
        self._joystick = None
        self.state = GamepadState()

    def init_sdl(self):
        """Initialize SDL2 game controller subsystem. Returns True on success."""
        import os
        try:
            import sdl2dll
            os.environ["PYSDL2_DLL_PATH"] = os.path.join(os.path.dirname(sdl2dll.__file__), "dll")
        except ImportError:
            pass
        import sdl2
        _init_maps()

        ret = sdl2.SDL_Init(sdl2.SDL_INIT_GAMECONTROLLER | sdl2.SDL_INIT_JOYSTICK)
        if ret < 0:
            return False
        num = sdl2.SDL_NumJoysticks()
        if num > 0:
            self._open(0)
        return True

    def _open(self, index):
        """Open game controller at given device index."""
        import sdl2

        if sdl2.SDL_IsGameController(index):
            gc = sdl2.SDL_GameControllerOpen(index)
            if gc:
                self._controller = gc
                self._joystick = sdl2.SDL_GameControllerGetJoystick(gc)
                self._use_fallback = False
                self._device_index = index
                self.state.connected = True
                name_bytes = sdl2.SDL_GameControllerName(gc)
                self.state.name = name_bytes.decode("utf-8", errors="replace") if name_bytes else f"Controller {index}"
                self._detect_type(index)
                return

        # Fallback to raw joystick if GameController mapping unavailable
        js = sdl2.SDL_JoystickOpen(index)
        if js:
            self._joystick = js
            self._controller = None
            self._use_fallback = True
            self._device_index = index
            self.state.connected = True
            name_bytes = sdl2.SDL_JoystickName(js)
            self.state.name = name_bytes.decode("utf-8", errors="replace") if name_bytes else f"Joystick {index}"
            self.state.controller_type = detect_controller_type(self.state.name)

    def _detect_type(self, index):
        """Detect controller type using SDL_GameControllerTypeForIndex or name."""
        import sdl2
        try:
            ctype = sdl2.SDL_GameControllerTypeForIndex(index)
            ps5 = getattr(sdl2, "SDL_CONTROLLER_TYPE_PS5", 7)
            xbox360 = getattr(sdl2, "SDL_CONTROLLER_TYPE_XBOX360", 1)
            xboxone = getattr(sdl2, "SDL_CONTROLLER_TYPE_XBOXONE", 2)
            if ctype == ps5:
                self.state.controller_type = ControllerType.DUALSENSE
                return
            if ctype in (xbox360, xboxone):
                self.state.controller_type = ControllerType.XBOX
                return
        except Exception:
            pass
        self.state.controller_type = detect_controller_type(self.state.name)

    def close(self):
        """Close current controller and quit SDL."""
        import sdl2

        if self._controller:
            sdl2.SDL_GameControllerClose(self._controller)
            self._controller = None
        if self._joystick and not self._controller:
            sdl2.SDL_JoystickClose(self._joystick)
        self._joystick = None
        self.state.connected = False
        sdl2.SDL_Quit()

    def poll(self):
        """Poll SDL events and read current controller state."""
        import sdl2

        sdl2.SDL_PumpEvents()

        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(event):
            etype = event.type
            if etype == sdl2.SDL_CONTROLLERDEVICEADDED:
                if not self.state.connected:
                    self._open(event.cdevice.which)
            elif etype == sdl2.SDL_CONTROLLERDEVICEREMOVED:
                if self._controller and sdl2.SDL_GameControllerInstanceID(self._controller) == event.cdevice.which:
                    sdl2.SDL_GameControllerClose(self._controller)
                    self._controller = None
                    self._joystick = None
                    self.state.connected = False
                    self.state.name = ""
                    self.state.controller_type = ControllerType.UNKNOWN
            elif etype == sdl2.SDL_JOYDEVICEADDED:
                if not self.state.connected and not self._controller:
                    self._open(event.jdevice.which)
            elif etype == sdl2.SDL_JOYDEVICEREMOVED:
                if self._joystick and not self._controller:
                    if sdl2.SDL_JoystickInstanceID(self._joystick) == event.jdevice.which:
                        sdl2.SDL_JoystickClose(self._joystick)
                        self._joystick = None
                        self.state.connected = False
                        self.state.name = ""
                        self.state.controller_type = ControllerType.UNKNOWN

        if not self._joystick and not self._controller:
            return self.state

        if self._use_fallback:
            self._poll_joystick_fallback()
        else:
            self._poll_gamecontroller()

        return self.state

    def _poll_gamecontroller(self):
        """Poll using SDL_GameController API (standardized mapping)."""
        import sdl2

        gc = self._controller
        if not gc:
            return

        for name, sdl_btn in _GC_BUTTON_MAP.items():
            self.state.buttons[name] = bool(sdl2.SDL_GameControllerGetButton(gc, sdl_btn))

        for name, sdl_axis in _GC_AXIS_MAP.items():
            raw = sdl2.SDL_GameControllerGetAxis(gc, sdl_axis)
            if name in ("lt", "rt"):
                self.state.axes[name] = normalize_trigger(raw)
            else:
                self.state.axes[name] = normalize_axis(raw)

    def _poll_joystick_fallback(self):
        """Poll using raw SDL_Joystick API (fallback for unmapped controllers)."""
        import sdl2

        js = self._joystick
        if not js:
            return

        # Use basic mapping: buttons 0-10, axes 0-5
        fallback_btn = [
            "a", "b", "x", "y", "lb", "rb",
            "back", "start", "guide", "ls_click", "rs_click",
        ]
        for i, name in enumerate(fallback_btn):
            self.state.buttons[name] = bool(sdl2.SDL_JoystickGetButton(js, i))

        # D-pad from hat
        hat_val = sdl2.SDL_JoystickGetHat(js, 0) if sdl2.SDL_JoystickNumHats(js) > 0 else 0
        self.state.buttons["dpad_up"] = bool(hat_val & sdl2.SDL_HAT_UP)
        self.state.buttons["dpad_down"] = bool(hat_val & sdl2.SDL_HAT_DOWN)
        self.state.buttons["dpad_left"] = bool(hat_val & sdl2.SDL_HAT_LEFT)
        self.state.buttons["dpad_right"] = bool(hat_val & sdl2.SDL_HAT_RIGHT)

        # Axes
        axis_map = [("ls_x", 0), ("ls_y", 1), ("rs_x", 2), ("rs_y", 3), ("lt", 4), ("rt", 5)]
        for name, idx in axis_map:
            raw = sdl2.SDL_JoystickGetAxis(js, idx)
            if name in ("lt", "rt"):
                self.state.axes[name] = normalize_trigger(raw)
            else:
                self.state.axes[name] = normalize_axis(raw)
