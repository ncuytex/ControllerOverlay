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
