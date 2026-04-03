import os
import sys

# Add src/ to path so controller_overlay package is importable
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from controller_overlay.gamepad import GamepadManager, ControllerType
from controller_overlay.overlay import ControllerOverlay
from controller_overlay.tray import TrayController
from controller_overlay.themes import make_theme_for_mode
from controller_overlay.config import load_config, save_config
from controller_overlay.translations import t, KEY_NOT_CONNECTED


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # keep running in tray

    # Init gamepad
    gamepad = GamepadManager()
    if not gamepad.init_sdl():
        print("Failed to initialize SDL2")
        sys.exit(1)

    # Load persisted config
    cfg = load_config()
    initial_theme = make_theme_for_mode(
        cfg["color_mode"], cfg.get("custom_colors", {})
    )

    # Create overlay with persisted theme
    overlay = ControllerOverlay(gamepad, initial_theme, opacity=0.9)
    overlay.show()

    # Mutable language reference so get_name() always uses current lang
    current_lang = ["zh-CN"]

    # Create tray
    def get_name():
        if gamepad.state.connected:
            ct = gamepad.state.controller_type
            type_str = {
                ControllerType.XBOX: "Xbox",
                ControllerType.DUALSENSE: "DualSense",
            }.get(ct, "Gamepad")
            return f"{gamepad.state.name} ({type_str})"
        return t(KEY_NOT_CONNECTED, current_lang[0])

    tray = TrayController(get_controller_name=get_name)
    tray.set_initial_state(cfg["color_mode"], cfg.get("custom_colors", {}))

    # Connect tray signals
    def on_theme_changed(theme):
        overlay.set_theme(theme)

    def on_opacity_changed(value):
        overlay.set_opacity(value)

    def on_position_changed(pos_x, pos_y):
        overlay.set_position(pos_x, pos_y)

    def on_scale_changed(scale):
        overlay.set_scale(scale)

    def on_language_changed(lang):
        current_lang[0] = lang
        overlay.set_language(lang)

    def on_color_mode_saved(mode, custom_colors):
        save_config(mode, custom_colors)

    def on_quit():
        gamepad.close()
        app.quit()

    tray.theme_changed.connect(on_theme_changed)
    tray.opacity_changed.connect(on_opacity_changed)
    tray.position_changed.connect(on_position_changed)
    tray.scale_changed.connect(on_scale_changed)
    tray.language_changed.connect(on_language_changed)
    tray.color_mode_saved.connect(on_color_mode_saved)
    tray.quit_requested.connect(on_quit)

    # Periodically update tray status (every 2s)
    status_timer = QTimer()
    status_timer.timeout.connect(tray.update_status)
    status_timer.start(2000)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
