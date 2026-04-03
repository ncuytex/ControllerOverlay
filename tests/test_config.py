import json
import os
import tempfile
from unittest import mock

from controller_overlay.config import load_config, save_config, CONFIG_FILENAME


def test_load_config_returns_defaults_when_no_file():
    with mock.patch("controller_overlay.config._config_path", return_value="/nonexistent/path/config.json"):
        cfg = load_config()
        assert cfg["color_mode"] == "classic"
        assert cfg["custom_colors"] == {}


def test_save_and_load_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, CONFIG_FILENAME)
        with mock.patch("controller_overlay.config._config_path", return_value=path):
            custom = {"a": "#FF0000", "b": "#00FF00"}
            save_config("custom", custom)
            cfg = load_config()
            assert cfg["color_mode"] == "custom"
            assert cfg["custom_colors"]["a"] == "#FF0000"
            assert cfg["custom_colors"]["b"] == "#00FF00"


def test_load_config_handles_corrupt_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, CONFIG_FILENAME)
        with open(path, "w") as f:
            f.write("NOT VALID JSON{{{")
        with mock.patch("controller_overlay.config._config_path", return_value=path):
            cfg = load_config()
            assert cfg["color_mode"] == "classic"
            assert cfg["custom_colors"] == {}


def test_load_config_handles_missing_keys():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, CONFIG_FILENAME)
        with open(path, "w") as f:
            json.dump({"color_mode": "red"}, f)
        with mock.patch("controller_overlay.config._config_path", return_value=path):
            cfg = load_config()
            assert cfg["color_mode"] == "red"
            assert cfg["custom_colors"] == {}


def test_save_config_file_content():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, CONFIG_FILENAME)
        with mock.patch("controller_overlay.config._config_path", return_value=path):
            save_config("blue", {"guide": "#0000FF"})
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert data["color_mode"] == "blue"
            assert data["custom_colors"]["guide"] == "#0000FF"
