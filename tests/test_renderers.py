from renderers import get_renderer, XboxRenderer, DualSenseRenderer
from gamepad import ControllerType


def test_xbox_renderer():
    r = get_renderer(ControllerType.XBOX)
    assert isinstance(r, XboxRenderer)


def test_dualsense_renderer():
    r = get_renderer(ControllerType.DUALSENSE)
    assert isinstance(r, DualSenseRenderer)


def test_unknown_falls_back_to_xbox():
    r = get_renderer(ControllerType.UNKNOWN)
    assert isinstance(r, XboxRenderer)


def test_renderer_is_singleton():
    """Same controller type returns the same renderer instance."""
    assert get_renderer(ControllerType.XBOX) is get_renderer(ControllerType.XBOX)
    assert get_renderer(ControllerType.DUALSENSE) is get_renderer(ControllerType.DUALSENSE)
