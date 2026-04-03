"""Tests for renderers.py — SVG element ID mappings and positioning data."""

from controller_overlay.gamepad import ControllerType
from controller_overlay.renderers import (
    BUTTON_MAPS, TRIGGER_OFFSETS, JOYSTICK_MAPS, STICK_CENTERS,
    XBOX_BUTTON_MAP, DS_BUTTON_MAP,
    XBOX_TRIGGER_OFFSETS, DS_TRIGGER_OFFSETS,
    XBOX_DPAD_CENTER, XBOX_DPAD_RADIUS,
)


def test_xbox_button_map_exists():
    bmap = BUTTON_MAPS[ControllerType.XBOX]
    assert bmap is XBOX_BUTTON_MAP


def test_ds_button_map_exists():
    bmap = BUTTON_MAPS[ControllerType.DUALSENSE]
    assert bmap is DS_BUTTON_MAP


def test_unknown_falls_back_to_xbox():
    bmap = BUTTON_MAPS[ControllerType.UNKNOWN]
    assert bmap is XBOX_BUTTON_MAP


def test_xbox_button_ids_are_lists():
    for name, ids in XBOX_BUTTON_MAP.items():
        assert isinstance(ids, list), f"{name}: expected list, got {type(ids)}"
        for eid in ids:
            assert isinstance(eid, str), f"{name}: element ID must be str"


def test_ds_button_ids_are_lists():
    for name, ids in DS_BUTTON_MAP.items():
        assert isinstance(ids, list), f"{name}: expected list, got {type(ids)}"
        for eid in ids:
            assert isinstance(eid, str)


def test_xbox_trigger_offsets_valid():
    for side in ('left', 'right'):
        off = XBOX_TRIGGER_OFFSETS[side]
        assert 0 < off['center_x_frac'] < 1
        assert 0 < off['width_frac'] < 1
        assert off['gap_px'] >= 0


def test_ds_trigger_offsets_valid():
    for side in ('left', 'right'):
        off = DS_TRIGGER_OFFSETS[side]
        assert 0 < off['center_x_frac'] < 1
        assert 0 < off['width_frac'] < 1
        assert off['gap_px'] >= 0


def test_trigger_offsets_for_all_types():
    for ctype in ControllerType:
        assert ctype in TRIGGER_OFFSETS


def test_stick_centers_valid():
    for ctype in ControllerType:
        centers = STICK_CENTERS[ctype]
        assert 'ls' in centers and 'rs' in centers
        for stick, (cx, cy) in centers.items():
            assert isinstance(cx, (int, float))
            assert isinstance(cy, (int, float))


def test_xbox_dpad_center_in_viewbox():
    cx, cy = XBOX_DPAD_CENTER
    # Xbox viewBox is 0 0 427 240
    assert 0 < cx < 427
    assert 0 < cy < 240
    assert XBOX_DPAD_RADIUS > 0
