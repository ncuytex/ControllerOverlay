import os
import sys

# Add src/ to path so controller_overlay package is importable
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from controller_overlay.gamepad import GamepadManager, ControllerType
from controller_overlay.overlay import ControllerOverlay
from controller_overlay.tray import TrayController
from controller_overlay.themes import THEMES


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # keep running in tray

    # Init gamepad
    gamepad = GamepadManager()
    if not gamepad.init_sdl():
        print("Failed to initialize SDL2")
        sys.exit(1)

    # Create overlay with default theme
    overlay = ControllerOverlay(gamepad, THEMES["white"], opacity=0.9)
    overlay.show()

    # Create tray
    def get_name():
        if gamepad.state.connected:
            ct = gamepad.state.controller_type
            type_str = {
                ControllerType.XBOX: "Xbox",
                ControllerType.DUALSENSE: "DualSense",
            }.get(ct, "Gamepad")
            return f"{gamepad.state.name} ({type_str})"
        return "未连接"

    tray = TrayController(get_controller_name=get_name)

    # Connect tray signals
    def on_theme_changed(name):
        overlay.set_theme(THEMES[name])

    def on_opacity_changed(value):
        overlay.set_opacity(value)

    def on_position_changed(pos_x, pos_y):
        overlay.set_position(pos_x, pos_y)

    def on_scale_changed(scale):
        overlay.set_scale(scale)

    def on_quit():
        gamepad.close()
        app.quit()

    tray.theme_changed.connect(on_theme_changed)
    tray.opacity_changed.connect(on_opacity_changed)
    tray.position_changed.connect(on_position_changed)
    tray.scale_changed.connect(on_scale_changed)
    tray.quit_requested.connect(on_quit)

    # Periodically update tray status (every 2s)
    status_timer = QTimer()
    status_timer.timeout.connect(tray.update_status)
    status_timer.start(2000)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
