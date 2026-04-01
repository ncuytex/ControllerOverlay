from gamepad import normalize_axis, DEADZONE_PERCENT, AXIS_MAX, BUTTON_MAP, AXIS_MAP


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


def test_button_mapping_keys():
    assert "a" in BUTTON_MAP
    assert "b" in BUTTON_MAP
    assert "x" in BUTTON_MAP
    assert "y" in BUTTON_MAP
    assert "lb" in BUTTON_MAP
    assert "rb" in BUTTON_MAP
    assert "start" in BUTTON_MAP
    assert "back" in BUTTON_MAP
    assert "guide" in BUTTON_MAP
    assert "ls_x" in AXIS_MAP
    assert "ls_y" in AXIS_MAP
    assert "rs_x" in AXIS_MAP
    assert "rs_y" in AXIS_MAP
    assert "lt" in AXIS_MAP
    assert "rt" in AXIS_MAP
