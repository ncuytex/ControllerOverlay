from PyQt5.QtWidgets import (
    QSystemTrayIcon, QMenu, QAction, QActionGroup,
    QDialog, QVBoxLayout, QHBoxLayout, QSlider, QSpinBox,
    QGroupBox, QFormLayout, QLabel, QPushButton,
    QComboBox, QCompleter,
)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen
from PyQt5.QtCore import QObject, pyqtSignal, Qt

from .themes import THEMES
from .translations import (
    t, DEFAULT_LANG,
    LANGUAGES,
    KEY_APP_NAME, KEY_CLOSE, KEY_COLOR_THEME, KEY_CONFIRM,
    KEY_CONTROLLER_STATUS, KEY_DISPLAY_SETTINGS,
    KEY_DISPLAY_SETTINGS_MENU, KEY_DISPLAY_SIZE,
    KEY_HORIZONTAL_POS, KEY_LANGUAGE,
    KEY_NOT_CONNECTED, KEY_OPACITY, KEY_POSITION_SETTINGS,
    KEY_QUIT, KEY_SELECT_LANGUAGE, KEY_SIZE_SETTINGS,
    KEY_VERTICAL_POS,
)


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


class LanguageDialog(QDialog):
    """Dialog for selecting the UI language."""

    language_selected = pyqtSignal(str)  # emits language code

    def __init__(self, current_lang, parent=None):
        super().__init__(parent)
        self._current_lang = current_lang
        self._apply_language()
        self.setFixedSize(320, 160)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)

        self._label = QLabel(t(KEY_SELECT_LANGUAGE, current_lang))
        layout.addWidget(self._label)

        # Language combo with search
        self._combo = QComboBox()
        self._combo.setEditable(True)
        self._combo.setInsertPolicy(QComboBox.NoInsert)
        completer = QCompleter(list(LANGUAGES.values()))
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self._combo.setCompleter(completer)
        for code, name in LANGUAGES.items():
            self._combo.addItem(name, code)
        # Set current selection
        idx = self._combo.findData(current_lang)
        if idx >= 0:
            self._combo.setCurrentIndex(idx)
        layout.addWidget(self._combo)

        # Confirm button
        self._confirm_btn = QPushButton(t(KEY_CONFIRM, current_lang))
        self._confirm_btn.clicked.connect(self._confirm)
        layout.addWidget(self._confirm_btn, alignment=Qt.AlignRight)

    def _confirm(self):
        code = self._combo.currentData()
        if code:
            self.language_selected.emit(code)
        self.hide()

    def set_language(self, lang):
        """Re-translate dialog labels."""
        self.setWindowTitle(t(KEY_LANGUAGE, lang))
        self._label.setText(t(KEY_SELECT_LANGUAGE, lang))
        self._confirm_btn.setText(t(KEY_CONFIRM, lang))
        self._current_lang = lang

    def _apply_language(self):
        self.setWindowTitle(t(KEY_LANGUAGE, self._current_lang))


class SettingsDialog(QDialog):
    """Dialog for adjusting overlay position and size."""

    position_changed = pyqtSignal(int, int)  # pos_x, pos_y (0-100)
    scale_changed = pyqtSignal(int)           # scale (0-100)

    def __init__(self, lang=DEFAULT_LANG, parent=None):
        super().__init__(parent)
        self._lang = lang
        self.setFixedSize(380, 340)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)

        # ---- Position group ----
        self._pos_group = QGroupBox(t(KEY_POSITION_SETTINGS, lang))
        pos_layout = QFormLayout()

        # Horizontal position
        h_layout = QHBoxLayout()
        self.h_slider = QSlider(Qt.Horizontal)
        self.h_slider.setRange(0, 100)
        self.h_slider.setValue(50)
        self.h_spin = QSpinBox()
        self.h_spin.setRange(0, 100)
        self.h_spin.setValue(50)
        self.h_spin.setFixedWidth(60)
        self.h_slider.valueChanged.connect(self.h_spin.setValue)
        self.h_spin.valueChanged.connect(self.h_slider.setValue)
        self.h_slider.valueChanged.connect(self._emit_position)
        self.h_spin.valueChanged.connect(self._emit_position)
        h_layout.addWidget(self.h_slider, 1)
        h_layout.addWidget(self.h_spin)
        self._h_label = t(KEY_HORIZONTAL_POS, lang)
        pos_layout.addRow(self._h_label, h_layout)

        # Vertical position
        v_layout = QHBoxLayout()
        self.v_slider = QSlider(Qt.Horizontal)
        self.v_slider.setRange(0, 100)
        self.v_slider.setValue(0)
        self.v_spin = QSpinBox()
        self.v_spin.setRange(0, 100)
        self.v_spin.setValue(0)
        self.v_spin.setFixedWidth(60)
        self.v_slider.valueChanged.connect(self.v_spin.setValue)
        self.v_spin.valueChanged.connect(self.v_slider.setValue)
        self.v_slider.valueChanged.connect(self._emit_position)
        self.v_spin.valueChanged.connect(self._emit_position)
        v_layout.addWidget(self.v_slider, 1)
        v_layout.addWidget(self.v_spin)
        self._v_label = t(KEY_VERTICAL_POS, lang)
        pos_layout.addRow(self._v_label, v_layout)

        self._pos_group.setLayout(pos_layout)
        layout.addWidget(self._pos_group)

        # ---- Size group ----
        self._size_group = QGroupBox(t(KEY_SIZE_SETTINGS, lang))
        size_layout = QFormLayout()

        s_layout = QHBoxLayout()
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(0, 100)
        self.size_slider.setValue(10)
        self.size_spin = QSpinBox()
        self.size_spin.setRange(0, 100)
        self.size_spin.setValue(10)
        self.size_spin.setFixedWidth(60)
        self.size_slider.valueChanged.connect(self.size_spin.setValue)
        self.size_spin.valueChanged.connect(self.size_slider.setValue)
        self.size_slider.valueChanged.connect(lambda v: self.scale_changed.emit(v))
        self.size_spin.valueChanged.connect(lambda v: self.scale_changed.emit(v))
        s_layout.addWidget(self.size_slider, 1)
        s_layout.addWidget(self.size_spin)
        self._s_label = t(KEY_DISPLAY_SIZE, lang)
        size_layout.addRow(self._s_label, s_layout)

        self._size_group.setLayout(size_layout)
        layout.addWidget(self._size_group)

        # Close button
        self._close_btn = QPushButton(t(KEY_CLOSE, lang))
        self._close_btn.clicked.connect(self.hide)
        layout.addWidget(self._close_btn, alignment=Qt.AlignRight)

        self._apply_language()

    def _apply_language(self):
        self.setWindowTitle(t(KEY_DISPLAY_SETTINGS, self._lang))

    def set_language(self, lang):
        """Re-translate all widget text."""
        self._lang = lang
        self.setWindowTitle(t(KEY_DISPLAY_SETTINGS, lang))
        self._pos_group.setTitle(t(KEY_POSITION_SETTINGS, lang))
        self._size_group.setTitle(t(KEY_SIZE_SETTINGS, lang))
        self._close_btn.setText(t(KEY_CLOSE, lang))
        # Update form labels — QFormLayout stores label as item
        pos_form = self._pos_group.layout()
        self._h_label = t(KEY_HORIZONTAL_POS, lang)
        self._v_label = t(KEY_VERTICAL_POS, lang)
        label_w = pos_form.itemAt(0, QFormLayout.LabelRole).widget()
        if label_w:
            label_w.setText(self._h_label)
        label_w = pos_form.itemAt(1, QFormLayout.LabelRole).widget()
        if label_w:
            label_w.setText(self._v_label)

        size_form = self._size_group.layout()
        self._s_label = t(KEY_DISPLAY_SIZE, lang)
        label_w = size_form.itemAt(0, QFormLayout.LabelRole).widget()
        if label_w:
            label_w.setText(self._s_label)

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
    language_changed = pyqtSignal(str)    # emits language code
    quit_requested = pyqtSignal()

    def __init__(self, get_controller_name=None):
        super().__init__()
        self._get_controller_name = get_controller_name or (lambda: t(KEY_NOT_CONNECTED, DEFAULT_LANG))
        self._current_opacity = 0.9
        self._current_theme = "white"
        self._current_language = DEFAULT_LANG
        self._settings_dialog = None
        self._language_dialog = None
        self._tray = QSystemTrayIcon(create_tray_icon())
        self._menu = QMenu()
        self._build_menu()
        self._tray.setContextMenu(self._menu)
        self._tray.setToolTip(
            f"{t(KEY_APP_NAME, self._current_language)} - {t(KEY_NOT_CONNECTED, self._current_language)}"
        )
        self._tray.show()

    def _build_menu(self):
        self._menu.clear()
        lang = self._current_language

        # Status line (non-clickable)
        status = QAction(
            f"{t(KEY_CONTROLLER_STATUS, lang)} {self._get_controller_name()}",
            self._menu,
        )
        status.setEnabled(False)
        self._menu.addAction(status)
        self._menu.addSeparator()

        # Display settings
        settings_act = self._menu.addAction(t(KEY_DISPLAY_SETTINGS_MENU, lang))
        settings_act.triggered.connect(self._open_settings)

        # Opacity submenu
        opacity_menu = self._menu.addMenu(t(KEY_OPACITY, lang))
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
        theme_menu = self._menu.addMenu(t(KEY_COLOR_THEME, lang))
        theme_group = QActionGroup(self)
        for name in THEMES:
            act = theme_menu.addAction(name)
            act.setData(name)
            act.setCheckable(True)
            act.setActionGroup(theme_group)
            if name == self._current_theme:
                act.setChecked(True)
            act.triggered.connect(lambda checked, n=name: self._set_theme(n))

        # Language menu action
        language_act = self._menu.addAction(t(KEY_LANGUAGE, lang))
        language_act.triggered.connect(self._open_language_dialog)

        self._menu.addSeparator()

        # Quit
        quit_act = self._menu.addAction(t(KEY_QUIT, lang))
        quit_act.triggered.connect(self.quit_requested.emit)

    def _set_opacity(self, value):
        self._current_opacity = value
        self.opacity_changed.emit(value)

    def _set_theme(self, name):
        self._current_theme = name
        self.theme_changed.emit(name)

    def _set_language(self, lang_code):
        self._current_language = lang_code
        self.language_changed.emit(lang_code)
        self._build_menu()
        if self._settings_dialog is not None:
            self._settings_dialog.set_language(lang_code)
        if self._language_dialog is not None:
            self._language_dialog.set_language(lang_code)

    def _open_settings(self):
        if self._settings_dialog is None:
            self._settings_dialog = SettingsDialog(self._current_language)
            self._settings_dialog.position_changed.connect(self.position_changed.emit)
            self._settings_dialog.scale_changed.connect(self.scale_changed.emit)
        self._settings_dialog.show()
        self._settings_dialog.raise_()
        self._settings_dialog.activateWindow()

    def _open_language_dialog(self):
        if self._language_dialog is None:
            self._language_dialog = LanguageDialog(self._current_language)
            self._language_dialog.language_selected.connect(self._set_language)
        self._language_dialog.show()
        self._language_dialog.raise_()
        self._language_dialog.activateWindow()

    def update_status(self):
        """Refresh tray tooltip and menu status line."""
        name = self._get_controller_name()
        lang = self._current_language
        nc = t(KEY_NOT_CONNECTED, lang)
        connected = name != nc and name != ""
        tooltip = f"{t(KEY_APP_NAME, lang)} - {name}" if connected else f"{t(KEY_APP_NAME, lang)} - {nc}"
        self._tray.setToolTip(tooltip)
        # Only rebuild menu when it is not currently visible to avoid flicker
        if not self._menu.isVisible():
            self._build_menu()
