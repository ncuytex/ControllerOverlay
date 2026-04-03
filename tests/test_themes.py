from controller_overlay.themes import (
    THEMES, Theme, COLOR_MODES, MONO_COLORS,
    make_theme_for_mode, _make_classic_colors, _make_mono_colors,
)

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


# --- Color mode tests ---

def test_color_modes_defined():
    assert COLOR_MODES == ["classic", "red", "green", "blue", "custom"]


def test_mono_colors_defined():
    assert set(MONO_COLORS.keys()) == {"red", "green", "blue"}
    for name, color in MONO_COLORS.items():
        assert color.startswith("#") and len(color) == 7


def test_make_classic_colors():
    colors = _make_classic_colors()
    # ABXY each has a distinct color
    face = {colors["a"], colors["b"], colors["x"], colors["y"]}
    assert len(face) == 4, "ABXY should have 4 distinct colors"
    # Shoulder pairs match
    assert colors["lb"] == colors["rb"]
    assert colors["lt"] == colors["rt"]
    # All required buttons present
    for btn in REQUIRED_HIGHLIGHTS:
        assert btn in colors, f"Missing {btn} in classic colors"


def test_make_mono_colors():
    colors = _make_mono_colors("#FF0000")
    for btn in REQUIRED_HIGHLIGHTS:
        assert colors[btn] == "#FF0000", f"{btn} should be #FF0000"


def test_make_theme_for_mode_classic():
    theme = make_theme_for_mode("classic")
    assert isinstance(theme, Theme)
    for btn in REQUIRED_HIGHLIGHTS:
        assert btn in theme.highlight


def test_make_theme_for_mode_monochrome():
    for mode in ("red", "green", "blue"):
        theme = make_theme_for_mode(mode)
        assert isinstance(theme, Theme)
        color = theme.highlight["a"]
        for btn in REQUIRED_HIGHLIGHTS:
            assert theme.highlight[btn] == color, f"{mode}: {btn} != a"


def test_make_theme_for_mode_custom():
    custom = {"a": "#FF0000", "b": "#00FF00"}
    theme = make_theme_for_mode("custom", custom_colors=custom)
    assert theme.highlight["a"] == "#FF0000"
    assert theme.highlight["b"] == "#00FF00"
    # Missing buttons filled from classic defaults
    assert "guide" in theme.highlight


def test_make_theme_for_mode_custom_empty():
    theme = make_theme_for_mode("custom", custom_colors=None)
    assert isinstance(theme, Theme)
    # Falls back to classic
    assert "a" in theme.highlight


def test_make_theme_for_mode_invalid_falls_back():
    theme = make_theme_for_mode("nonexistent")
    assert isinstance(theme, Theme)
    assert "a" in theme.highlight
