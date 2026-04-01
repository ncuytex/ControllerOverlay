from gamepad import (
    normalize_axis, normalize_trigger,
    DEADZONE_PERCENT, AXIS_MAX,
    BUTTON_NAMES, AXIS_NAMES,
    ControllerType, detect_controller_type,
)


def test_normalize_axis_center():
    assert normalize_axis(0) == 0.0


def test_normalize_axis_full_right():
    result = normalize_axis(AXIS_MAX)
    assert abs(result - 1.0) < 0.01


def test_normalize_axis_full_left():
    result = normalize_axis(-AXIS_MAX)
    assert abs(result - (-1.0)) < 0.01


def test_normalize_axis_deadzone_center_region():
    threshold = int(AXIS_MAX * DEADZONE_PERCENT)
    assert normalize_axis(threshold - 1) == 0.0
    assert normalize_axis(-(threshold - 1)) == 0.0
    assert normalize_axis(threshold) != 0.0


def test_normalize_axis_deadzone_rescales():
    threshold = int(AXIS_MAX * DEADZONE_PERCENT)
    result = normalize_axis(threshold + 100)
    assert 0.0 < result < 0.1


def test_normalize_trigger_zero():
    assert normalize_trigger(0) == 0.0


def test_normalize_trigger_max():
    result = normalize_trigger(AXIS_MAX)
    assert abs(result - 1.0) < 0.01


def test_normalize_trigger_deadzone():
    threshold = int(AXIS_MAX * DEADZONE_PERCENT)
    assert normalize_trigger(threshold - 1) == 0.0
    assert normalize_trigger(threshold + 1) != 0.0


def test_normalize_trigger_positive_only():
    """Trigger values are always in [0, 32767]."""
    assert normalize_trigger(0) == 0.0
    assert normalize_trigger(AXIS_MAX) > 0.0


def test_button_names():
    expected = {
        "a", "b", "x", "y", "lb", "rb",
        "back", "start", "guide",
        "ls_click", "rs_click",
        "dpad_up", "dpad_down", "dpad_left", "dpad_right",
        "misc1", "touchpad",
    }
    assert set(BUTTON_NAMES) == expected


def test_axis_names():
    expected = {"ls_x", "ls_y", "rs_x", "rs_y", "lt", "rt"}
    assert set(AXIS_NAMES) == expected


def test_controller_type_enum():
    assert ControllerType.XBOX.value == "xbox"
    assert ControllerType.DUALSENSE.value == "dualsense"
    assert ControllerType.UNKNOWN.value == "unknown"


def test_detect_xbox():
    assert detect_controller_type("Microsoft X-Box One S pad") == ControllerType.XBOX
    assert detect_controller_type("Xbox Series Controller") == ControllerType.XBOX
    assert detect_controller_type("XInput Controller") == ControllerType.XBOX


def test_detect_dualsense():
    assert detect_controller_type("DualSense Wireless Controller") == ControllerType.DUALSENSE
    assert detect_controller_type("Sony PS5 Controller") == ControllerType.DUALSENSE


def test_detect_unknown_defaults_xbox():
    assert detect_controller_type("Generic USB Gamepad") == ControllerType.XBOX
