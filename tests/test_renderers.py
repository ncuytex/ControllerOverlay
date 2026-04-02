from renderers import BUTTON_LAYOUTS, XBOX_BUTTONS, DS_BUTTONS, XBOX_STICKS, DS_STICKS
from gamepad import ControllerType


def test_xbox_layout_exists():
    buttons, sticks = BUTTON_LAYOUTS[ControllerType.XBOX]
    assert buttons is XBOX_BUTTONS
    assert sticks is XBOX_STICKS


def test_dualsense_layout_exists():
    buttons, sticks = BUTTON_LAYOUTS[ControllerType.DUALSENSE]
    assert buttons is DS_BUTTONS
    assert sticks is DS_STICKS


def test_unknown_falls_back_to_xbox():
    buttons, sticks = BUTTON_LAYOUTS[ControllerType.UNKNOWN]
    assert buttons is XBOX_BUTTONS


def test_xbox_buttons_have_areas():
    required = {"a", "b", "x", "y", "lb", "rb", "lt", "rt",
                "dpad_up", "dpad_down", "dpad_left", "dpad_right",
                "back", "start", "guide", "ls_click", "rs_click"}
    assert required.issubset(set(XBOX_BUTTONS.keys()))
    for name, (x, y, w, h, shape) in XBOX_BUTTONS.items():
        assert shape in ("ellipse", "roundrect")
        assert w > 0 and h > 0


def test_ds_buttons_have_areas():
    required = {"a", "b", "x", "y", "lb", "rb", "lt", "rt",
                "dpad_up", "dpad_down", "dpad_left", "dpad_right",
                "back", "start", "guide", "touchpad", "misc1",
                "ls_click", "rs_click"}
    assert required.issubset(set(DS_BUTTONS.keys()))
    for name, (x, y, w, h, shape) in DS_BUTTONS.items():
        assert shape in ("ellipse", "roundrect")
        assert w > 0 and h > 0


def test_sticks_have_center_and_diameter():
    for name, (cx, cy, d) in XBOX_STICKS.items():
        assert d > 0
    for name, (cx, cy, d) in DS_STICKS.items():
        assert d > 0
