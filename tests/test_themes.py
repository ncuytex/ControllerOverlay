from themes import THEMES, Theme

REQUIRED_HIGHLIGHTS = (
    "a", "b", "x", "y", "lb", "rb", "lt", "rt",
    "dpad_up", "dpad_down", "dpad_left", "dpad_right",
    "ls_click", "rs_click",
    "start", "back", "guide",
    "misc1", "touchpad",
)


def test_all_themes_have_required_highlights():
    for name, theme in THEMES.items():
        assert isinstance(theme, Theme)
        for btn in REQUIRED_HIGHLIGHTS:
            assert btn in theme.highlight, f"Missing highlight for {btn} in {name}"


def test_three_themes_exist():
    assert set(THEMES.keys()) == {"white", "black", "neon"}


def test_highlight_colors_are_valid_hex():
    for name, theme in THEMES.items():
        for btn, color in theme.highlight.items():
            assert color.startswith("#"), f"{name}.{btn} highlight not hex"
            assert len(color) == 7, f"{name}.{btn} highlight wrong length"
