from PyQt5.QtWidgets import (
    QSystemTrayIcon, QMenu, QAction, QActionGroup,
    QDialog, QVBoxLayout, QHBoxLayout, QSlider, QSpinBox,
    QGroupBox, QFormLayout, QLabel, QPushButton,
)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen
from PyQt5.QtCore import QObject, pyqtSignal, Qt

from .themes import THEMES


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


class SettingsDialog(QDialog):
    """Dialog for adjusting overlay position and size."""

    position_changed = pyqtSignal(int, int)  # pos_x, pos_y (0-100)
    scale_changed = pyqtSignal(int)           # scale (0-100)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("显示设置")
        self.setFixedSize(380, 340)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)

        # ---- Position group ----
        pos_group = QGroupBox("位置设置")
        pos_layout = QFormLayout()

        # Horizontal position
        h_layout = QHBoxLayout()
        self.h_slider = QSlider(Qt.Horizontal)
        self.h_slider.setRange(0, 100)
        self.h_slider.setValue(90)
        self.h_spin = QSpinBox()
        self.h_spin.setRange(0, 100)
        self.h_spin.setValue(90)
        self.h_spin.setFixedWidth(60)
        self.h_slider.valueChanged.connect(self.h_spin.setValue)
        self.h_spin.valueChanged.connect(self.h_slider.setValue)
        self.h_slider.valueChanged.connect(self._emit_position)
        self.h_spin.valueChanged.connect(self._emit_position)
        h_layout.addWidget(self.h_slider, 1)
        h_layout.addWidget(self.h_spin)
        pos_layout.addRow("水平位置 (0-100):", h_layout)

        # Vertical position
        v_layout = QHBoxLayout()
        self.v_slider = QSlider(Qt.Horizontal)
        self.v_slider.setRange(0, 100)
        self.v_slider.setValue(85)
        self.v_spin = QSpinBox()
        self.v_spin.setRange(0, 100)
        self.v_spin.setValue(85)
        self.v_spin.setFixedWidth(60)
        self.v_slider.valueChanged.connect(self.v_spin.setValue)
        self.v_spin.valueChanged.connect(self.v_slider.setValue)
        self.v_slider.valueChanged.connect(self._emit_position)
        self.v_spin.valueChanged.connect(self._emit_position)
        v_layout.addWidget(self.v_slider, 1)
        v_layout.addWidget(self.v_spin)
        pos_layout.addRow("垂直位置 (0-100):", v_layout)

        pos_group.setLayout(pos_layout)
        layout.addWidget(pos_group)

        # ---- Size group ----
        size_group = QGroupBox("大小设置")
        size_layout = QFormLayout()

        s_layout = QHBoxLayout()
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(0, 100)
        self.size_slider.setValue(30)
        self.size_spin = QSpinBox()
        self.size_spin.setRange(0, 100)
        self.size_spin.setValue(30)
        self.size_spin.setFixedWidth(60)
        self.size_slider.valueChanged.connect(self.size_spin.setValue)
        self.size_spin.valueChanged.connect(self.size_slider.setValue)
        self.size_slider.valueChanged.connect(lambda v: self.scale_changed.emit(v))
        self.size_spin.valueChanged.connect(lambda v: self.scale_changed.emit(v))
        s_layout.addWidget(self.size_slider, 1)
        s_layout.addWidget(self.size_spin)
        size_layout.addRow("显示大小 (0=隐藏, 100=全屏):", s_layout)

        size_group.setLayout(size_layout)
        layout.addWidget(size_group)

        # Close button
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)

    def _emit_position(self):
        self.position_changed.emit(self.h_slider.value(), self.v_slider.value())

    def set_values(self, pos_x, pos_y, scale):
        """Update dialog controls without triggering signals."""
        self.h_slider.blockSignals(True)
        self.h_spin.blockSignals(True)
        self.v_slider.blockSignals(True)
        self.v_spin.blockSignals(True)
        self.size_slider.blockSignals(True)
        self.size_spin.blockSignals(True)

        self.h_slider.setValue(pos_x)
        self.h_spin.setValue(pos_x)
        self.v_slider.setValue(pos_y)
        self.v_spin.setValue(pos_y)
        self.size_slider.setValue(scale)
        self.size_spin.setValue(scale)

        self.h_slider.blockSignals(False)
        self.h_spin.blockSignals(False)
        self.v_slider.blockSignals(False)
        self.v_spin.blockSignals(False)
        self.size_slider.blockSignals(False)
        self.size_spin.blockSignals(False)


class TrayController(QObject):
    """System tray icon with context menu for settings."""

    theme_changed = pyqtSignal(str)      # emits theme name
    opacity_changed = pyqtSignal(float)  # emits opacity value
    position_changed = pyqtSignal(int, int)  # emits pos_x, pos_y
    scale_changed = pyqtSignal(int)       # emits scale value
    quit_requested = pyqtSignal()

    def __init__(self, get_controller_name=None):
        super().__init__()
        self._get_controller_name = get_controller_name or (lambda: "未连接")
        self._current_opacity = 0.9
        self._current_theme = "white"
        self._settings_dialog = None
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

        # Display settings
        settings_act = self._menu.addAction("显示设置...")
        settings_act.triggered.connect(self._open_settings)

        # Opacity submenu
        opacity_menu = self._menu.addMenu("透明度")
        opacity_group = QActionGroup(self)
        for label, value in [("100%", 0.9), ("80%", 0.72), ("60%", 0.54)]:
            act = opacity_menu.addAction(label)
            act.setData(value)
            act.setCheckable(True)
            act.setActionGroup(opacity_group)
            if value == self._current_opacity:
                act.setChecked(True)
            act.triggered.connect(lambda checked, v=value: self._set_opacity(v))

        # Theme submenu
        theme_menu = self._menu.addMenu("配色主题")
        theme_group = QActionGroup(self)
        for name in THEMES:
            act = theme_menu.addAction(name)
            act.setData(name)
            act.setCheckable(True)
            act.setActionGroup(theme_group)
            if name == self._current_theme:
                act.setChecked(True)
            act.triggered.connect(lambda checked, n=name: self._set_theme(n))

        self._menu.addSeparator()

        # Quit
        quit_act = self._menu.addAction("退出")
        quit_act.triggered.connect(self.quit_requested.emit)

    def _set_opacity(self, value):
        self._current_opacity = value
        self.opacity_changed.emit(value)

    def _set_theme(self, name):
        self._current_theme = name
        self.theme_changed.emit(name)

    def _open_settings(self):
        if self._settings_dialog is None:
            self._settings_dialog = SettingsDialog()
            self._settings_dialog.position_changed.connect(self.position_changed.emit)
            self._settings_dialog.scale_changed.connect(self.scale_changed.emit)
        self._settings_dialog.show()
        self._settings_dialog.raise_()
        self._settings_dialog.activateWindow()

    def update_status(self):
        """Refresh tray tooltip and menu status line."""
        name = self._get_controller_name()
        connected = name != "未连接" and name != ""
        tooltip = f"手柄投影 - {name}" if connected else "手柄投影 - 未连接"
        self._tray.setToolTip(tooltip)
        self._build_menu()
