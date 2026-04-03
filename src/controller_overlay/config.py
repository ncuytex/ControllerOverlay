"""JSON-based configuration persistence for ControllerOverlay."""

import json
import os
import sys
import tempfile

CONFIG_FILENAME = "overlay_config.json"

_DEFAULT_CONFIG = {
    "color_mode": "classic",
    "custom_colors": {},
}


def _config_dir():
    """Return the directory where config is stored (project root, same as assets/ parent)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    # __file__ = <project_root>/src/controller_overlay/config.py
    return os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )


def _config_path():
    return os.path.join(_config_dir(), CONFIG_FILENAME)


def load_config():
    """Load config from JSON file. Returns safe defaults if missing or corrupt."""
    path = _config_path()
    if not os.path.exists(path):
        return dict(_DEFAULT_CONFIG)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Validate required keys
        if not isinstance(data, dict):
            return dict(_DEFAULT_CONFIG)
        data.setdefault("color_mode", _DEFAULT_CONFIG["color_mode"])
        data.setdefault("custom_colors", _DEFAULT_CONFIG["custom_colors"])
        return data
    except (json.JSONDecodeError, OSError):
        return dict(_DEFAULT_CONFIG)


def save_config(color_mode, custom_colors):
    """Atomically write config to JSON file."""
    data = {
        "color_mode": color_mode,
        "custom_colors": custom_colors,
    }
    path = _config_path()
    dir_path = os.path.dirname(path)
    try:
        # Atomic write: write to temp file, then rename
        fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, path)
        except BaseException:
            os.unlink(tmp_path)
            raise
    except OSError:
        # Fallback: direct write
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
