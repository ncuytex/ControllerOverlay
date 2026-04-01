from dataclasses import dataclass, field


@dataclass
class Theme:
    body_fill: str
    outline: str
    btn_default: str
    highlight: dict  # button_name -> color_hex


def _xbox_colors(base):
    """Standard Xbox ABXY colors (green, red, blue, yellow)."""
    return {
        "a": "#2ECC71" if base == "light" else "#3DFF8F" if base == "dark" else "#00FFAA",
        "b": "#E74C3C" if base == "light" else "#FF4D6A" if base == "dark" else "#FF0066",
        "x": "#3498FF" if base == "light" else "#5CB8FF" if base == "dark" else "#00AAFF",
        "y": "#F1C40F" if base == "light" else "#FFE04D" if base == "dark" else "#FFD700",
    }


def _dualsense_colors(base):
    """PlayStation face button colors: Cross=blue, Circle=red, Square=pink, Triangle=green."""
    return {
        "a": "#3498FF" if base == "light" else "#5CB8FF" if base == "dark" else "#00AAFF",
        "b": "#E74C3C" if base == "light" else "#FF4D6A" if base == "dark" else "#FF0066",
        "x": "#E91E8C" if base == "light" else "#FF66B2" if base == "dark" else "#FF00AA",
        "y": "#2ECC71" if base == "light" else "#3DFF8F" if base == "dark" else "#00FFAA",
    }


def _make_theme(body, outline, btn_default, base):
    colors = _xbox_colors(base)
    return Theme(
        body_fill=body,
        outline=outline,
        btn_default=btn_default,
        highlight={
            # Face buttons
            "a": colors["a"], "b": colors["b"], "x": colors["x"], "y": colors["y"],
            # Bumpers & triggers
            "lb": colors["b"], "rb": colors["x"],
            "lt": colors["b"], "rt": colors["x"],
            # D-pad (old compat key + new individual keys)
            "dpad": outline,
            "dpad_up": outline, "dpad_down": outline,
            "dpad_left": outline, "dpad_right": outline,
            # Sticks
            "ls": colors["x"], "rs": colors["a"],
            "ls_click": colors["x"], "rs_click": colors["a"],
            # Menu buttons
            "start": colors["a"], "back": colors["b"], "guide": colors["y"],
            # DualSense-specific
            "misc1": "#FF8C00" if base == "light" else "#FFA500" if base == "dark" else "#FF6600",
            "touchpad": outline,
        },
    )


THEMES = {
    "white": _make_theme("#E8E8E8", "#999999", "#CCCCCC", "light"),
    "black": _make_theme("#2A2A2A", "#666666", "#555555", "dark"),
    "neon":  _make_theme("#1A1A2E", "#4A4AFF", "#333366", "neon"),
}
