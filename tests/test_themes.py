# tests/test_themes.py
import pytest
from themes import THEMES, Theme


def test_all_themes_have_required_fields():
    for name, theme in THEMES.items():
        assert isinstance(theme, Theme)
        assert len(theme.body_fill) == 7  # "#RRGGBB"
        assert len(theme.outline) == 7
        assert len(theme.btn_default) == 7
        for btn in ("a", "b", "x", "y", "lb", "rb", "lt", "rt",
                     "dpad", "ls", "rs", "start", "back", "guide"):
            assert btn in theme.highlight, f"Missing highlight for {btn} in {name}"


def test_three_themes_exist():
    assert set(THEMES.keys()) == {"white", "black", "neon"}


def test_highlight_colors_are_valid_hex():
    for name, theme in THEMES.items():
        for btn, color in theme.highlight.items():
            assert color.startswith("#"), f"{name}.{btn} highlight not hex"
            assert len(color) == 7, f"{name}.{btn} highlight wrong length"
