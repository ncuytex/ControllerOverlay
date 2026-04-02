"""SVG element ID mappings and trigger positioning data.

Maps gamepad logical button names to SVG element IDs/classes,
provides joystick element references, and defines trigger placement
offsets relative to the main controller SVG.
"""

from gamepad import ControllerType

# ---------------------------------------------------------------------------
# Button → SVG element ID mappings
# Each value is a list of element IDs whose attributes should be modified.
# For Xbox, elements are stroke-only outlines.
# For DualSense, elements are filled shapes.
# ---------------------------------------------------------------------------

XBOX_BUTTON_MAP = {
    "a":        ["A"],
    "b":        ["B"],
    "x":        ["X"],
    "y":        ["Y"],
    "lb":       ["LB_top"],
    "rb":       [],                       # No explicit RB element
    "back":     ["View"],
    "start":    ["Menu"],
    "guide":    ["XBOX"],
    "share":    ["Share"],
    "ls_click": [],                       # Handled via class
    "rs_click": [],                       # Handled via class
    # D-pad handled separately via _apply_dpad_highlight
}

# D-pad center in Xbox SVG coordinate space (approximate bounding box of D_Pad)
XBOX_DPAD_CENTER = (168, 123)
XBOX_DPAD_RADIUS = 26

# Joystick class names and order info for Xbox SVG
# Left_Stick: 2 paths, Right_Stick: 2 paths
# inner=smaller, outer=larger (determined by bounding box area)
XBOX_STICK_CLASSES = {
    "ls": "Left_Stick",
    "rs": "Right_Stick",
}

DS_BUTTON_MAP = {
    "a":        ["Cross"],
    "b":        ["Circle"],
    "x":        ["Square"],
    "y":        ["Triangle"],
    "lb":       ["L1_Top"],
    "rb":       ["R1_Top"],
    "back":     [],                       # No Create element in SVG
    "start":    [],                       # No Options element in SVG
    "guide":    ["PS"],
    "touchpad": ["Touchpad"],
    "misc1":    ["Mic_Mute"],
    "ls_click": ["Left_Stick_Outer", "Left_Stick_Inner"],
    "rs_click": ["Right_Stick_Outer", "Right_Stick_Inner"],
    "dpad_up":    ["DPad_Up"],
    "dpad_down":  ["DPad_Down"],
    "dpad_left":  ["DPad_Left"],
    "dpad_right": ["DPad_Right"],
}

DS_JOYSTICK_MAP = {
    "ls": {"outer": "Left_Stick_Outer", "inner": "Left_Stick_Inner"},
    "rs": {"outer": "Right_Stick_Outer", "inner": "Right_Stick_Inner"},
}

# DualSense stick centers in SVG coords (128x128 viewBox)
# Derived from element geometry
DS_STICK_CENTERS = {
    "ls": (45.5, 64.5),
    "rs": (82.5, 64.5),
}

# ---------------------------------------------------------------------------
# Trigger placement offsets
# Defined as fractions of the main SVG viewBox dimensions.
# (x_fraction, y_offset_px, width_fraction)
# Triggers are positioned ABOVE the shoulder buttons.
# ---------------------------------------------------------------------------

# Xbox: LB_top is at roughly x=271-323 out of 427
# Symmetric RB at roughly x=104-156
XBOX_TRIGGER_OFFSETS = {
    "left": {
        "center_x_frac": 297.0 / 427.0,    # Center of LB_top
        "width_frac":     52.0 / 427.0,      # Shoulder width
        "gap_px":         2,                  # Gap above shoulder
    },
    "right": {
        "center_x_frac": 130.0 / 427.0,     # Symmetric to left
        "width_frac":     52.0 / 427.0,
        "gap_px":         2,
    },
}

# DualSense: L1_Top at roughly x=22-36 out of 128, R1_Top at 92-106
DS_TRIGGER_OFFSETS = {
    "left": {
        "center_x_frac": 29.0 / 128.0,
        "width_frac":     14.0 / 128.0,
        "gap_px":         2,
    },
    "right": {
        "center_x_frac": 99.0 / 128.0,
        "width_frac":     14.0 / 128.0,
        "gap_px":         2,
    },
}

# ---------------------------------------------------------------------------
# Lookup by controller type
# ---------------------------------------------------------------------------

BUTTON_MAPS = {
    ControllerType.XBOX:      XBOX_BUTTON_MAP,
    ControllerType.DUALSENSE: DS_BUTTON_MAP,
    ControllerType.UNKNOWN:   XBOX_BUTTON_MAP,
}

TRIGGER_OFFSETS = {
    ControllerType.XBOX:      XBOX_TRIGGER_OFFSETS,
    ControllerType.DUALSENSE: DS_TRIGGER_OFFSETS,
    ControllerType.UNKNOWN:   XBOX_TRIGGER_OFFSETS,
}

JOYSTICK_MAPS = {
    ControllerType.XBOX:      XBOX_STICK_CLASSES,
    ControllerType.DUALSENSE: DS_JOYSTICK_MAP,
    ControllerType.UNKNOWN:   XBOX_STICK_CLASSES,
}

STICK_CENTERS = {
    ControllerType.XBOX:      {"ls": (124, 64), "rs": (260, 117)},
    ControllerType.DUALSENSE: DS_STICK_CENTERS,
    ControllerType.UNKNOWN:   {"ls": (124, 64), "rs": (260, 117)},
}
