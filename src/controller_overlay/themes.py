from dataclasses import dataclass


@dataclass
class Theme:
    highlight: dict  # button_name -> color_hex


def _make_highlight_colors(variant):
    """Create highlight color map for all buttons."""
    if variant == "light":
        face = {"a": "#2ECC71", "b": "#E74C3C", "x": "#3498FF", "y": "#F1C40F"}
    elif variant == "dark":
        face = {"a": "#3DFF8F", "b": "#FF4D6A", "x": "#5CB8FF", "y": "#FFE04D"}
    else:  # neon
        face = {"a": "#00FFAA", "b": "#FF0066", "x": "#00AAFF", "y": "#FFD700"}

    return {
        **face,
        "lb": face["b"], "rb": face["x"],
        "lt": face["b"], "rt": face["x"],
        "dpad_up": face["x"], "dpad_down": face["x"],
        "dpad_left": face["x"], "dpad_right": face["x"],
        "ls_click": face["x"], "rs_click": face["a"],
        "back": face["b"], "start": face["a"], "guide": "#006FCD",
        "touchpad": face["x"], "misc1": "#FF8C00",
    }


THEMES = {
    "white": Theme(highlight=_make_highlight_colors("light")),
    "black": Theme(highlight=_make_highlight_colors("dark")),
    "neon":  Theme(highlight=_make_highlight_colors("neon")),
}

# ---------------------------------------------------------------------------
# Color mode system
# ---------------------------------------------------------------------------

COLOR_MODES = ["classic", "red", "green", "blue", "custom"]

MONO_COLORS = {
    "red":   "#E74C3C",
    "green": "#2ECC71",
    "blue":  "#3498FF",
}

_ALL_BUTTON_NAMES = [
    "a", "b", "x", "y",
    "lb", "rb", "lt", "rt",
    "back", "start", "guide",
    "ls_click", "rs_click",
    "dpad_up", "dpad_down", "dpad_left", "dpad_right",
    "misc1", "touchpad",
]


def _make_classic_colors():
    """Create the 经典 (Classic) highlight map with symmetric color assignment.

    ABXY: red / green / blue / yellow (each independent).
    D-pad: each direction gets its own matching color.
    Shoulder/trigger pairs share a color.
    Other buttons match the classic scheme.
    """
    return {
        # Face buttons — four distinct colors
        "a": "#2ECC71", "b": "#E74C3C", "x": "#3498FF", "y": "#F1C40F",
        # Shoulder pairs
        "lb": "#9B59B6", "rb": "#9B59B6",
        "lt": "#9B59B6", "rt": "#9B59B6",
        # D-pad — each direction a distinct color
        "dpad_up":    "#E74C3C",
        "dpad_down":  "#2ECC71",
        "dpad_left":  "#3498FF",
        "dpad_right": "#F1C40F",
        # Stick clicks
        "ls_click": "#3498FF", "rs_click": "#2ECC71",
        # Menu buttons
        "back": "#E74C3C", "start": "#2ECC71", "guide": "#006FCD",
        # DualSense-specific
        "touchpad": "#3498FF", "misc1": "#FF8C00",
    }


def _make_mono_colors(hex_color):
    """Create a highlight map where every button uses the same color."""
    return {name: hex_color for name in _ALL_BUTTON_NAMES}


def make_theme_for_mode(mode, custom_colors=None):
    """Return a Theme for the given color mode string.

    mode: one of COLOR_MODES ("classic", "red", "green", "blue", "custom")
    custom_colors: dict of button_name -> hex (required when mode=="custom")
    """
    if mode == "classic":
        return Theme(highlight=_make_classic_colors())
    elif mode in MONO_COLORS:
        return Theme(highlight=_make_mono_colors(MONO_COLORS[mode]))
    elif mode == "custom":
        if custom_colors:
            # Fill any missing buttons with the classic default
            base = _make_classic_colors()
            base.update(custom_colors)
            return Theme(highlight=base)
        else:
            return Theme(highlight=_make_classic_colors())
    else:
        return Theme(highlight=_make_classic_colors())
