from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QActionGroup
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen
from PyQt5.QtCore import QObject, pyqtSignal, Qt

from themes import THEMES


def create_tray_icon():
    """Create a simple gamepad icon for the system tray."""
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(0, 0, 0, 0))
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.Antialiasing)
    # Controller body
    p.setBrush(QColor("#4A9EFF"))
    p.setPen(QPen(QColor("#5AB8FF"), 2))
    p.drawRoundedRect(8, 18, 48, 28, 10, 10)
    # Left grip
    p.drawRoundedRect(4, 30, 18, 22, 6, 6)
    # Right grip
    p.drawRoundedRect(42, 30, 18, 22, 6, 6)
    # Dpad dot
    p.setBrush(QColor("#FFFFFF"))
    p.setPen(Qt.NoPen)
    p.drawEllipse(20, 28, 6, 6)
    # Buttons dots
    p.drawEllipse(38, 26, 5, 5)
    p.drawEllipse(44, 32, 5, 5)
    p.end()
    return QIcon(pixmap)


class TrayController(QObject):
    """System tray icon with context menu for settings."""

    theme_changed = pyqtSignal(str)      # emits theme name
    opacity_changed = pyqtSignal(float)  # emits opacity value
    quit_requested = pyqtSignal()

    def __init__(self, get_controller_name=None):
        super().__init__()
        self._get_controller_name = get_controller_name or (lambda: "未连接")
        self._tray = QSystemTrayIcon(create_tray_icon())
        self._menu = QMenu()
        self._build_menu()
        self._tray.setContextMenu(self._menu)
        self._tray.setToolTip("手柄投影 - 未连接")
        self._tray.show()

    def _build_menu(self):
        self._menu.clear()

        # Status line (non-clickable)
        status = QAction(f"手柄: {self._get_controller_name()}", self._menu)
        status.setEnabled(False)
        self._menu.addAction(status)
        self._menu.addSeparator()

        # Opacity submenu
        opacity_menu = self._menu.addMenu("透明度")
        opacity_group = QActionGroup(self)
        for label, value in [("100%", 0.9), ("80%", 0.72), ("60%", 0.54)]:
            act = opacity_menu.addAction(label)
            act.setData(value)
            act.setCheckable(True)
            act.setActionGroup(opacity_group)
            if value == 0.9:
                act.setChecked(True)
            act.triggered.connect(lambda checked, v=value: self.opacity_changed.emit(v))

        # Theme submenu
        theme_menu = self._menu.addMenu("配色主题")
        theme_group = QActionGroup(self)
        for name in THEMES:
            act = theme_menu.addAction(name)
            act.setData(name)
            act.setCheckable(True)
            act.setActionGroup(theme_group)
            if name == "white":
                act.setChecked(True)
            act.triggered.connect(lambda checked, n=name: self.theme_changed.emit(n))

        self._menu.addSeparator()

        # Quit
        quit_act = self._menu.addAction("退出")
        quit_act.triggered.connect(self.quit_requested.emit)

    def update_status(self):
        """Refresh tray tooltip and menu status line."""
        name = self._get_controller_name()
        connected = name != "未连接" and name != ""
        tooltip = f"手柄投影 - {name}" if connected else "手柄投影 - 未连接"
        self._tray.setToolTip(tooltip)
        self._build_menu()
