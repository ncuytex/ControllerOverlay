"""Translation data module for ControllerOverlay."""

# ---------------------------------------------------------------------------
# String key constants
# ---------------------------------------------------------------------------
KEY_APP_NAME = "app_name"
KEY_CLOSE = "close"
KEY_COLOR_THEME = "color_theme"
KEY_CONFIRM = "confirm"
KEY_CONTROLLER_STATUS = "controller_status"
KEY_DISPLAY_SETTINGS = "display_settings"
KEY_DISPLAY_SETTINGS_MENU = "display_settings_menu"
KEY_DISPLAY_SIZE = "display_size"
KEY_HORIZONTAL_POS = "horizontal_pos"
KEY_LANGUAGE = "language"
KEY_NO_CONTROLLER = "no_controller"
KEY_NOT_CONNECTED = "not_connected"
KEY_OPACITY = "opacity"
KEY_POSITION_SETTINGS = "position_settings"
KEY_QUIT = "quit"
KEY_SELECT_LANGUAGE = "select_language"
KEY_SIZE_SETTINGS = "size_settings"
KEY_VERTICAL_POS = "vertical_pos"

# ---------------------------------------------------------------------------
# Language registry: code → native name
# ---------------------------------------------------------------------------
LANGUAGES = {
    "en": "English",
    "zh-CN": "简体中文",
    "hi": "हिन्दी",
    "es": "Español",
    "ar": "العربية",
    "fr": "Français",
    "pt": "Português",
    "ru": "Русский",
    "id": "Bahasa Indonesia",
    "zh-TW": "繁體中文",
    "de": "Deutsch",
    "ja": "日本語",
    "vi": "Tiếng Việt",
    "tr": "Türkçe",
    "ko": "한국어",
}

# Reverse lookup: native name → code
LANG_CODE_BY_NAME = {v: k for k, v in LANGUAGES.items()}

# ---------------------------------------------------------------------------
# Default language
# ---------------------------------------------------------------------------
DEFAULT_LANG = "zh-CN"

# ---------------------------------------------------------------------------
# Font fallbacks per language (Windows built-in fonts)
# ---------------------------------------------------------------------------
FONT_FALLBACKS = {
    "zh-CN": "Microsoft YaHei",
    "zh-TW": "Microsoft JhengHei",
    "ja": "Yu Gothic",
    "ko": "Malgun Gothic",
    "hi": "Nirmala UI",
    "ar": "Segoe UI",
}


def get_font(lang: str) -> str:
    """Return a suitable font family for the given language."""
    return FONT_FALLBACKS.get(lang, "Segoe UI")


# ---------------------------------------------------------------------------
# Translation table: LANG_CODE → { KEY → translated string }
# ---------------------------------------------------------------------------
TRANSLATIONS = {
    "en": {
        KEY_APP_NAME: "Controller Overlay",
        KEY_CLOSE: "Close",
        KEY_COLOR_THEME: "Color Theme",
        KEY_CONFIRM: "OK",
        KEY_CONTROLLER_STATUS: "Controller:",
        KEY_DISPLAY_SETTINGS: "Display Settings",
        KEY_DISPLAY_SETTINGS_MENU: "Display Settings...",
        KEY_DISPLAY_SIZE: "Display Size (0=Hidden, 100=Fullscreen):",
        KEY_HORIZONTAL_POS: "Horizontal Position (0-100):",
        KEY_LANGUAGE: "Language",
        KEY_NO_CONTROLLER: "No Controller Connected",
        KEY_NOT_CONNECTED: "Not Connected",
        KEY_OPACITY: "Opacity",
        KEY_POSITION_SETTINGS: "Position",
        KEY_QUIT: "Quit",
        KEY_SELECT_LANGUAGE: "Select Language:",
        KEY_SIZE_SETTINGS: "Size",
        KEY_VERTICAL_POS: "Vertical Position (0-100):",
    },
    "zh-CN": {
        KEY_APP_NAME: "手柄投影",
        KEY_CLOSE: "关闭",
        KEY_COLOR_THEME: "配色主题",
        KEY_CONFIRM: "确定",
        KEY_CONTROLLER_STATUS: "手柄:",
        KEY_DISPLAY_SETTINGS: "显示设置",
        KEY_DISPLAY_SETTINGS_MENU: "显示设置...",
        KEY_DISPLAY_SIZE: "显示大小 (0=隐藏, 100=全屏):",
        KEY_HORIZONTAL_POS: "水平位置 (0-100):",
        KEY_LANGUAGE: "语言",
        KEY_NO_CONTROLLER: "未连接手柄",
        KEY_NOT_CONNECTED: "未连接",
        KEY_OPACITY: "透明度",
        KEY_POSITION_SETTINGS: "位置设置",
        KEY_QUIT: "退出",
        KEY_SELECT_LANGUAGE: "选择语言:",
        KEY_SIZE_SETTINGS: "大小设置",
        KEY_VERTICAL_POS: "垂直位置 (0-100):",
    },
    "hi": {
        KEY_APP_NAME: "कंट्रोलर ओवरले",
        KEY_CLOSE: "बंद करें",
        KEY_COLOR_THEME: "रंग थीम",
        KEY_CONFIRM: "ठीक है",
        KEY_CONTROLLER_STATUS: "कंट्रोलर:",
        KEY_DISPLAY_SETTINGS: "प्रदर्शन सेटिंग",
        KEY_DISPLAY_SETTINGS_MENU: "प्रदर्शन सेटिंग...",
        KEY_DISPLAY_SIZE: "प्रदर्शन आकार (0=छिपा, 100=पूर्ण स्क्रीन):",
        KEY_HORIZONTAL_POS: "क्षैतिज स्थिति (0-100):",
        KEY_LANGUAGE: "भाषा",
        KEY_NO_CONTROLLER: "कंट्रोलर कनेक्ट नहीं है",
        KEY_NOT_CONNECTED: "कनेक्ट नहीं है",
        KEY_OPACITY: "अस्पष्टता",
        KEY_POSITION_SETTINGS: "स्थिति सेटिंग",
        KEY_QUIT: "बाहर निकलें",
        KEY_SELECT_LANGUAGE: "भाषा चुनें:",
        KEY_SIZE_SETTINGS: "आकार सेटिंग",
        KEY_VERTICAL_POS: "लंबवत स्थिति (0-100):",
    },
    "es": {
        KEY_APP_NAME: "Superposición de Mando",
        KEY_CLOSE: "Cerrar",
        KEY_COLOR_THEME: "Tema de Color",
        KEY_CONFIRM: "Aceptar",
        KEY_CONTROLLER_STATUS: "Mando:",
        KEY_DISPLAY_SETTINGS: "Ajustes de Pantalla",
        KEY_DISPLAY_SETTINGS_MENU: "Ajustes de Pantalla...",
        KEY_DISPLAY_SIZE: "Tamaño (0=Oculto, 100=Pantalla completa):",
        KEY_HORIZONTAL_POS: "Posición Horizontal (0-100):",
        KEY_LANGUAGE: "Idioma",
        KEY_NO_CONTROLLER: "Mando No Conectado",
        KEY_NOT_CONNECTED: "No Conectado",
        KEY_OPACITY: "Opacidad",
        KEY_POSITION_SETTINGS: "Posición",
        KEY_QUIT: "Salir",
        KEY_SELECT_LANGUAGE: "Seleccionar Idioma:",
        KEY_SIZE_SETTINGS: "Tamaño",
        KEY_VERTICAL_POS: "Posición Vertical (0-100):",
    },
    "ar": {
        KEY_APP_NAME: "تراكب وحدة التحكم",
        KEY_CLOSE: "إغلاق",
        KEY_COLOR_THEME: "سمة الألوان",
        KEY_CONFIRM: "موافق",
        KEY_CONTROLLER_STATUS: "وحدة التحكم:",
        KEY_DISPLAY_SETTINGS: "إعدادات العرض",
        KEY_DISPLAY_SETTINGS_MENU: "إعدادات العرض...",
        KEY_DISPLAY_SIZE: "حجم العرض (0=مخفي، 100=ملء الشاشة):",
        KEY_HORIZONTAL_POS: "الموضع الأفقي (0-100):",
        KEY_LANGUAGE: "اللغة",
        KEY_NO_CONTROLLER: "وحدة التحكم غير متصلة",
        KEY_NOT_CONNECTED: "غير متصل",
        KEY_OPACITY: "الشفافية",
        KEY_POSITION_SETTINGS: "الموضع",
        KEY_QUIT: "إنهاء",
        KEY_SELECT_LANGUAGE: "اختر اللغة:",
        KEY_SIZE_SETTINGS: "الحجم",
        KEY_VERTICAL_POS: "الموضع العمودي (0-100):",
    },
    "fr": {
        KEY_APP_NAME: "Overlay Manette",
        KEY_CLOSE: "Fermer",
        KEY_COLOR_THEME: "Thème de Couleur",
        KEY_CONFIRM: "OK",
        KEY_CONTROLLER_STATUS: "Manette :",
        KEY_DISPLAY_SETTINGS: "Paramètres d'Affichage",
        KEY_DISPLAY_SETTINGS_MENU: "Paramètres d'Affichage...",
        KEY_DISPLAY_SIZE: "Taille d'Affichage (0=Masqué, 100=Plein écran) :",
        KEY_HORIZONTAL_POS: "Position Horizontale (0-100) :",
        KEY_LANGUAGE: "Langue",
        KEY_NO_CONTROLLER: "Manette Non Connectée",
        KEY_NOT_CONNECTED: "Non Connecté",
        KEY_OPACITY: "Opacité",
        KEY_POSITION_SETTINGS: "Position",
        KEY_QUIT: "Quitter",
        KEY_SELECT_LANGUAGE: "Sélectionner la Langue :",
        KEY_SIZE_SETTINGS: "Taille",
        KEY_VERTICAL_POS: "Position Verticale (0-100) :",
    },
    "pt": {
        KEY_APP_NAME: "Sobreposição de Controle",
        KEY_CLOSE: "Fechar",
        KEY_COLOR_THEME: "Tema de Cores",
        KEY_CONFIRM: "OK",
        KEY_CONTROLLER_STATUS: "Controle:",
        KEY_DISPLAY_SETTINGS: "Configurações de Exibição",
        KEY_DISPLAY_SETTINGS_MENU: "Configurações de Exibição...",
        KEY_DISPLAY_SIZE: "Tamanho (0=Oculto, 100=Tela Cheia):",
        KEY_HORIZONTAL_POS: "Posição Horizontal (0-100):",
        KEY_LANGUAGE: "Idioma",
        KEY_NO_CONTROLLER: "Controle Não Conectado",
        KEY_NOT_CONNECTED: "Não Conectado",
        KEY_OPACITY: "Opacidade",
        KEY_POSITION_SETTINGS: "Posição",
        KEY_QUIT: "Sair",
        KEY_SELECT_LANGUAGE: "Selecionar Idioma:",
        KEY_SIZE_SETTINGS: "Tamanho",
        KEY_VERTICAL_POS: "Posição Vertical (0-100):",
    },
    "ru": {
        KEY_APP_NAME: "Оверлей Контроллера",
        KEY_CLOSE: "Закрыть",
        KEY_COLOR_THEME: "Цветовая Тема",
        KEY_CONFIRM: "ОК",
        KEY_CONTROLLER_STATUS: "Контроллер:",
        KEY_DISPLAY_SETTINGS: "Настройки Отображения",
        KEY_DISPLAY_SETTINGS_MENU: "Настройки Отображения...",
        KEY_DISPLAY_SIZE: "Размер (0=Скрыть, 100=Полный экран):",
        KEY_HORIZONTAL_POS: "Горизонтальная Позиция (0-100):",
        KEY_LANGUAGE: "Язык",
        KEY_NO_CONTROLLER: "Контроллер Не Подключён",
        KEY_NOT_CONNECTED: "Не Подключён",
        KEY_OPACITY: "Непрозрачность",
        KEY_POSITION_SETTINGS: "Позиция",
        KEY_QUIT: "Выход",
        KEY_SELECT_LANGUAGE: "Выбрать Язык:",
        KEY_SIZE_SETTINGS: "Размер",
        KEY_VERTICAL_POS: "Вертикальная Позиция (0-100):",
    },
    "id": {
        KEY_APP_NAME: "Overlay Pengontrol",
        KEY_CLOSE: "Tutup",
        KEY_COLOR_THEME: "Tema Warna",
        KEY_CONFIRM: "OK",
        KEY_CONTROLLER_STATUS: "Pengontrol:",
        KEY_DISPLAY_SETTINGS: "Pengaturan Tampilan",
        KEY_DISPLAY_SETTINGS_MENU: "Pengaturan Tampilan...",
        KEY_DISPLAY_SIZE: "Ukuran Tampilan (0=Sembunyikan, 100=Layar Penuh):",
        KEY_HORIZONTAL_POS: "Posisi Horizontal (0-100):",
        KEY_LANGUAGE: "Bahasa",
        KEY_NO_CONTROLLER: "Pengontrol Tidak Terhubung",
        KEY_NOT_CONNECTED: "Tidak Terhubung",
        KEY_OPACITY: "Opasitas",
        KEY_POSITION_SETTINGS: "Posisi",
        KEY_QUIT: "Keluar",
        KEY_SELECT_LANGUAGE: "Pilih Bahasa:",
        KEY_SIZE_SETTINGS: "Ukuran",
        KEY_VERTICAL_POS: "Posisi Vertikal (0-100):",
    },
    "zh-TW": {
        KEY_APP_NAME: "手柄投影",
        KEY_CLOSE: "關閉",
        KEY_COLOR_THEME: "配色主題",
        KEY_CONFIRM: "確定",
        KEY_CONTROLLER_STATUS: "手柄:",
        KEY_DISPLAY_SETTINGS: "顯示設定",
        KEY_DISPLAY_SETTINGS_MENU: "顯示設定...",
        KEY_DISPLAY_SIZE: "顯示大小 (0=隱藏, 100=全螢幕):",
        KEY_HORIZONTAL_POS: "水平位置 (0-100):",
        KEY_LANGUAGE: "語言",
        KEY_NO_CONTROLLER: "未連接手柄",
        KEY_NOT_CONNECTED: "未連接",
        KEY_OPACITY: "透明度",
        KEY_POSITION_SETTINGS: "位置設定",
        KEY_QUIT: "退出",
        KEY_SELECT_LANGUAGE: "選擇語言:",
        KEY_SIZE_SETTINGS: "大小設定",
        KEY_VERTICAL_POS: "垂直位置 (0-100):",
    },
    "de": {
        KEY_APP_NAME: "Controller-Overlay",
        KEY_CLOSE: "Schließen",
        KEY_COLOR_THEME: "Farbschema",
        KEY_CONFIRM: "OK",
        KEY_CONTROLLER_STATUS: "Controller:",
        KEY_DISPLAY_SETTINGS: "Anzeigeeinstellungen",
        KEY_DISPLAY_SETTINGS_MENU: "Anzeigeeinstellungen...",
        KEY_DISPLAY_SIZE: "Anzeigegröße (0=Ausblenden, 100=Vollbild):",
        KEY_HORIZONTAL_POS: "Horizontale Position (0-100):",
        KEY_LANGUAGE: "Sprache",
        KEY_NO_CONTROLLER: "Controller Nicht Verbunden",
        KEY_NOT_CONNECTED: "Nicht Verbunden",
        KEY_OPACITY: "Deckkraft",
        KEY_POSITION_SETTINGS: "Position",
        KEY_QUIT: "Beenden",
        KEY_SELECT_LANGUAGE: "Sprache Auswählen:",
        KEY_SIZE_SETTINGS: "Größe",
        KEY_VERTICAL_POS: "Vertikale Position (0-100):",
    },
    "ja": {
        KEY_APP_NAME: "コントローラーオーバーレイ",
        KEY_CLOSE: "閉じる",
        KEY_COLOR_THEME: "カラーテーマ",
        KEY_CONFIRM: "OK",
        KEY_CONTROLLER_STATUS: "コントローラー:",
        KEY_DISPLAY_SETTINGS: "表示設定",
        KEY_DISPLAY_SETTINGS_MENU: "表示設定...",
        KEY_DISPLAY_SIZE: "表示サイズ (0=非表示, 100=全画面):",
        KEY_HORIZONTAL_POS: "水平位置 (0-100):",
        KEY_LANGUAGE: "言語",
        KEY_NO_CONTROLLER: "コントローラー未接続",
        KEY_NOT_CONNECTED: "未接続",
        KEY_OPACITY: "不透明度",
        KEY_POSITION_SETTINGS: "位置",
        KEY_QUIT: "終了",
        KEY_SELECT_LANGUAGE: "言語を選択:",
        KEY_SIZE_SETTINGS: "サイズ",
        KEY_VERTICAL_POS: "垂直位置 (0-100):",
    },
    "vi": {
        KEY_APP_NAME: "Lớp Phủ Tay Cầm",
        KEY_CLOSE: "Đóng",
        KEY_COLOR_THEME: "Chủ Đề Màu",
        KEY_CONFIRM: "OK",
        KEY_CONTROLLER_STATUS: "Tay Cầm:",
        KEY_DISPLAY_SETTINGS: "Cài Đặt Hiển Thị",
        KEY_DISPLAY_SETTINGS_MENU: "Cài Đặt Hiển Thị...",
        KEY_DISPLAY_SIZE: "Kích Thước (0=Ẩn, 100=Toàn Màn Hình):",
        KEY_HORIZONTAL_POS: "Vị Trí Ngang (0-100):",
        KEY_LANGUAGE: "Ngôn Ngữ",
        KEY_NO_CONTROLLER: "Tay Cầm Chưa Kết Nối",
        KEY_NOT_CONNECTED: "Chưa Kết Nối",
        KEY_OPACITY: "Độ Mờ",
        KEY_POSITION_SETTINGS: "Vị Trí",
        KEY_QUIT: "Thoát",
        KEY_SELECT_LANGUAGE: "Chọn Ngôn Ngữ:",
        KEY_SIZE_SETTINGS: "Kích Thước",
        KEY_VERTICAL_POS: "Vị Trí Dọc (0-100):",
    },
    "tr": {
        KEY_APP_NAME: "Kontrolcü Katmanı",
        KEY_CLOSE: "Kapat",
        KEY_COLOR_THEME: "Renk Teması",
        KEY_CONFIRM: "Tamam",
        KEY_CONTROLLER_STATUS: "Kontrolcü:",
        KEY_DISPLAY_SETTINGS: "Görünüm Ayarları",
        KEY_DISPLAY_SETTINGS_MENU: "Görünüm Ayarları...",
        KEY_DISPLAY_SIZE: "Görünüm Boyutu (0=Gizle, 100=Tam Ekran):",
        KEY_HORIZONTAL_POS: "Yatay Konum (0-100):",
        KEY_LANGUAGE: "Dil",
        KEY_NO_CONTROLLER: "Kontrolcü Bağlı Değil",
        KEY_NOT_CONNECTED: "Bağlı Değil",
        KEY_OPACITY: "Opaklık",
        KEY_POSITION_SETTINGS: "Konum",
        KEY_QUIT: "Çıkış",
        KEY_SELECT_LANGUAGE: "Dil Seç:",
        KEY_SIZE_SETTINGS: "Boyut",
        KEY_VERTICAL_POS: "Dikey Konum (0-100):",
    },
    "ko": {
        KEY_APP_NAME: "컨트롤러 오버레이",
        KEY_CLOSE: "닫기",
        KEY_COLOR_THEME: "색상 테마",
        KEY_CONFIRM: "확인",
        KEY_CONTROLLER_STATUS: "컨트롤러:",
        KEY_DISPLAY_SETTINGS: "표시 설정",
        KEY_DISPLAY_SETTINGS_MENU: "표시 설정...",
        KEY_DISPLAY_SIZE: "표시 크기 (0=숨김, 100=전체 화면):",
        KEY_HORIZONTAL_POS: "가로 위치 (0-100):",
        KEY_LANGUAGE: "언어",
        KEY_NO_CONTROLLER: "컨트롤러 연결 안 됨",
        KEY_NOT_CONNECTED: "연결 안 됨",
        KEY_OPACITY: "불투명도",
        KEY_POSITION_SETTINGS: "위치",
        KEY_QUIT: "종료",
        KEY_SELECT_LANGUAGE: "언어 선택:",
        KEY_SIZE_SETTINGS: "크기",
        KEY_VERTICAL_POS: "세로 위치 (0-100):",
    },
}

# All defined keys (for validation)
_ALL_KEYS = {k for lang_dict in TRANSLATIONS.values() for k in lang_dict}


def t(key: str, lang: str) -> str:
    """Return translated string for *key* in *lang*, with fallback."""
    return (
        TRANSLATIONS.get(lang, {}).get(key)
        or TRANSLATIONS.get(DEFAULT_LANG, {}).get(key)
        or key
    )
