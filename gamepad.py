DEADZONE_PERCENT = 0.05
AXIS_MAX = 32767

BUTTON_MAP = {
    "a": 0, "b": 1, "x": 2, "y": 3,
    "lb": 4, "rb": 5,
    "back": 6, "start": 7, "guide": 8,
}

AXIS_MAP = {
    "ls_x": 0, "ls_y": 1,
    "rs_x": 2, "rs_y": 3,
    "lt": 4, "rt": 5,
}

HAT_MAP = {
    "dpad": 0,
}


def normalize_axis(value):
    """Normalize a raw SDL2 axis value to [-1.0, 1.0] with deadzone applied."""
    threshold = int(AXIS_MAX * DEADZONE_PERCENT)
    if -threshold < value < threshold:
        return 0.0
    if value > threshold:
        return (value - threshold) / (AXIS_MAX - threshold)
    else:
        return (value + threshold) / (AXIS_MAX - threshold)


class GamepadState:
    """Snapshot of all gamepad inputs at a point in time."""

    def __init__(self):
        self.buttons = {name: False for name in BUTTON_MAP}
        self.axes = {name: 0.0 for name in AXIS_MAP}
        self.hats = {name: (0, 0) for name in HAT_MAP}
        self.connected = False
        self.name = ""


class GamepadManager:
    """Manages SDL2 joystick detection and state polling."""

    def __init__(self):
        self._joystick = None
        self._device_index = -1
        self.state = GamepadState()

    def init_sdl(self):
        """Initialize SDL2 joystick subsystem. Returns True on success."""
        import sdl2

        ret = sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)
        if ret < 0:
            return False
        num = sdl2.SDL_NumJoysticks()
        if num > 0:
            self._open(0)
        return True

    def _open(self, index):
        """Open joystick at given device index."""
        import sdl2

        js = sdl2.SDL_JoystickOpen(index)
        if js:
            self._joystick = js
            self._device_index = index
            self.state.connected = True
            name_bytes = sdl2.SDL_JoystickName(js)
            self.state.name = name_bytes.decode("utf-8", errors="replace") if name_bytes else f"Gamepad {index}"

    def close(self):
        """Close current joystick and quit SDL."""
        import sdl2

        if self._joystick:
            sdl2.SDL_JoystickClose(self._joystick)
            self._joystick = None
        self.state.connected = False
        sdl2.SDL_Quit()

    def poll(self):
        """Poll SDL events and read current joystick state."""
        import sdl2

        sdl2.SDL_PumpEvents()

        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(event):
            if event.type == sdl2.SDL_JOYDEVICEADDED:
                if not self.state.connected:
                    self._open(event.jdevice.which)
            elif event.type == sdl2.SDL_JOYDEVICEREMOVED:
                if self._joystick and sdl2.SDL_JoystickInstanceID(self._joystick) == event.jdevice.which:
                    sdl2.SDL_JoystickClose(self._joystick)
                    self._joystick = None
                    self.state.connected = False
                    self.state.name = ""

        if not self._joystick:
            return self.state

        for name, idx in BUTTON_MAP.items():
            self.state.buttons[name] = bool(sdl2.SDL_JoystickGetButton(self._joystick, idx))

        for name, idx in AXIS_MAP.items():
            raw = sdl2.SDL_JoystickGetAxis(self._joystick, idx)
            self.state.axes[name] = normalize_axis(raw)

        for name, idx in HAT_MAP.items():
            hat_val = sdl2.SDL_JoystickGetHat(self._joystick, idx)
            x = 0
            y = 0
            if hat_val & sdl2.SDL_HAT_UP:
                y = -1
            if hat_val & sdl2.SDL_HAT_DOWN:
                y = 1
            if hat_val & sdl2.SDL_HAT_LEFT:
                x = -1
            if hat_val & sdl2.SDL_HAT_RIGHT:
                x = 1
            self.state.hats[name] = (x, y)

        return self.state
