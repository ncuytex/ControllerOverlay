from gamepad import ControllerType

# ---------------------------------------------------------------------------
# Stick visual offset (in SVG coordinate units)
# ---------------------------------------------------------------------------
STICK_MAX_OFFSET = 15

# ---------------------------------------------------------------------------
# Button highlight areas: (x, y, w, h, shape)
#   shape: "ellipse" for round buttons, "roundrect" for rectangular
#   All coordinates are in SVG viewBox units
#   *** YOU MUST ADJUST THESE TO MATCH YOUR SVG ***
# ---------------------------------------------------------------------------

XBOX_BUTTONS = {
    # Face buttons (diamond layout, right side)
    "a": (307, 106, 26, 26, "ellipse"),    # bottom
    "b": (335, 83, 26, 26, "ellipse"),     # right
    "x": (280, 83, 26, 26, "ellipse"),     # left
    "y": (307, 60, 26, 26, "ellipse"),     # top
    # Bumpers
    "lb": (78, 40, 72, 14, "roundrect"),
    "rb": (277, 40, 72, 14, "roundrect"),
    # Triggers (highlight when axis > threshold)
    "lt": (86, 18, 62, 18, "roundrect"),
    "rt": (279, 18, 62, 18, "roundrect"),
    # D-pad (left side)
    "dpad_up": (126, 142, 18, 24, "roundrect"),
    "dpad_down": (126, 170, 18, 24, "roundrect"),
    "dpad_left": (108, 154, 24, 18, "roundrect"),
    "dpad_right": (138, 154, 24, 18, "roundrect"),
    # Menu buttons (center)
    "back": (183, 74, 16, 12, "ellipse"),   # View
    "start": (240, 74, 16, 12, "ellipse"),  # Menu
    "guide": (206, 56, 24, 18, "ellipse"),  # Xbox button
    # Stick clicks
    "ls_click": (117, 85, 44, 44, "ellipse"),
    "rs_click": (237, 132, 44, 44, "ellipse"),
}

XBOX_STICKS = {
    # (center_x, center_y, highlight_diameter) — for movement dot
    "ls": (139, 107, 36),
    "rs": (259, 154, 36),
}

DS_BUTTONS = {
    # Face buttons □ × ○ △ (diamond layout, right side)
    "a": (588, 270, 40, 40, "ellipse"),    # ×
    "b": (634, 228, 40, 40, "ellipse"),    # ○
    "x": (542, 228, 40, 40, "ellipse"),    # □
    "y": (588, 186, 40, 40, "ellipse"),    # △
    # Bumpers
    "lb": (150, 68, 130, 26, "roundrect"),
    "rb": (552, 68, 130, 26, "roundrect"),
    # Triggers
    "lt": (164, 30, 110, 34, "roundrect"),
    "rt": (558, 30, 110, 34, "roundrect"),
    # D-pad (left side)
    "dpad_up": (230, 244, 28, 38, "roundrect"),
    "dpad_down": (230, 298, 28, 38, "roundrect"),
    "dpad_left": (196, 266, 38, 28, "roundrect"),
    "dpad_right": (254, 266, 38, 28, "roundrect"),
    # Create / Options / PS
    "back": (315, 164, 40, 24, "roundrect"),    # Create
    "start": (478, 164, 40, 24, "roundrect"),   # Options
    "guide": (416, 308, 30, 30, "ellipse"),     # PS button
    # Touchpad / Mic
    "touchpad": (340, 130, 152, 60, "roundrect"),
    "misc1": (416, 380, 26, 26, "ellipse"),     # Mic
    # Stick clicks
    "ls_click": (210, 384, 60, 60, "ellipse"),
    "rs_click": (562, 384, 60, 60, "ellipse"),
}

DS_STICKS = {
    "ls": (240, 394, 50),
    "rs": (592, 394, 50),
}

# ---------------------------------------------------------------------------
# Lookup by controller type
# ---------------------------------------------------------------------------
BUTTON_LAYOUTS = {
    ControllerType.XBOX: (XBOX_BUTTONS, XBOX_STICKS),
    ControllerType.DUALSENSE: (DS_BUTTONS, DS_STICKS),
    ControllerType.UNKNOWN: (XBOX_BUTTONS, XBOX_STICKS),
}
