"""
Менеджер тем UTILHELP
Поддержка тёмной и светлой темы через глобальный QSS
"""
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from logger import log_info


# ─── Цветовые палитры ────────────────────────────────────────────────────────

DARK = {
    "bg_main":        "#1a1a1a",
    "bg_secondary":   "#2d2d2d",
    "bg_tertiary":    "#252525",
    "bg_card":        "#2d2d2d",
    "bg_input":       "#404040",
    "bg_hover":       "#4a4a4a",
    "bg_pressed":     "#555555",
    "bg_button":      "#404040",
    "bg_sidebar":     "#2d2d2d",
    "bg_titlebar":    "#2d2d2d",
    "text_primary":   "#ffffff",
    "text_secondary": "#cccccc",
    "text_disabled":  "#888888",
    "text_hint":      "#aaaaaa",
    "border":         "#404040",
    "border_hover":   "#555555",
    "border_light":   "#2d2d2d",
    "scrollbar_bg":   "#252525",
    "scrollbar_handle": "#555555",
    "scrollbar_hover":  "#666666",
    "accent":         "#4a9eff",
    "accent_hover":   "#5aafff",
    "success":        "#4CAF50",
    "error":          "#e74c3c",
    "warning":        "#f39c12",
    "card_border":    "#404040",
    "news_bg":        "#252525",
    "download_btn":   "#666666",
    "download_hover": "#777777",
    "download_press": "#555555",
}

LIGHT = {
    "bg_main":        "#f0f2f5",
    "bg_secondary":   "#ffffff",
    "bg_tertiary":    "#e8eaed",
    "bg_card":        "#ffffff",
    "bg_input":       "#e8eaed",
    "bg_hover":       "#dde1e7",
    "bg_pressed":     "#c8cdd5",
    "bg_button":      "#e8eaed",
    "bg_sidebar":     "#ffffff",
    "bg_titlebar":    "#ffffff",
    "text_primary":   "#1a1a2e",
    "text_secondary": "#444444",
    "text_disabled":  "#999999",
    "text_hint":      "#666666",
    "border":         "#d0d4db",
    "border_hover":   "#b0b8c4",
    "border_light":   "#e8eaed",
    "scrollbar_bg":   "#e8eaed",
    "scrollbar_handle": "#b0b8c4",
    "scrollbar_hover":  "#909aaa",
    "accent":         "#1a73e8",
    "accent_hover":   "#1557b0",
    "success":        "#2e7d32",
    "error":          "#c62828",
    "warning":        "#e65100",
    "card_border":    "#d0d4db",
    "news_bg":        "#f8f9fa",
    "download_btn":   "#5a6a7a",
    "download_hover": "#4a5a6a",
    "download_press": "#3a4a5a",
}


def _build_qss(c: dict) -> str:
    """Собрать глобальный QSS из палитры цветов"""
    return f"""
/* ── Базовые виджеты ── */
QWidget {{
    background-color: {c['bg_main']};
    color: {c['text_primary']};
    font-family: 'Segoe UI', Arial, sans-serif;
}}

QMainWindow, QDialog {{
    background-color: {c['bg_main']};
}}

/* ── Скроллбары ── */
QScrollBar:vertical {{
    background-color: {c['scrollbar_bg']};
    width: 16px;
    border-radius: 0px;
}}
QScrollBar::handle:vertical {{
    background-color: {c['scrollbar_handle']};
    border-radius: 8px;
    min-height: 30px;
    margin: 2px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {c['scrollbar_hover']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    border: none;
    background: transparent;
    height: 0px;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: {c['scrollbar_bg']};
}}
QScrollBar:horizontal {{
    background-color: {c['scrollbar_bg']};
    height: 16px;
    border-radius: 0px;
}}
QScrollBar::handle:horizontal {{
    background-color: {c['scrollbar_handle']};
    border-radius: 8px;
    min-width: 30px;
    margin: 2px;
}}
QScrollBar::handle:horizontal:hover {{
    background-color: {c['scrollbar_hover']};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    border: none;
    background: transparent;
    width: 0px;
}}

/* ── Кнопки ── */
QPushButton {{
    background-color: {c['bg_button']};
    color: {c['text_primary']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: {c['bg_hover']};
    border-color: {c['border_hover']};
}}
QPushButton:pressed {{
    background-color: {c['bg_pressed']};
}}
QPushButton:disabled {{
    background-color: {c['bg_tertiary']};
    color: {c['text_disabled']};
    border-color: {c['border_light']};
}}

/* ── Поля ввода ── */
QLineEdit {{
    background-color: {c['bg_input']};
    color: {c['text_primary']};
    border: 1px solid {c['border']};
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 13px;
    selection-background-color: {c['accent']};
}}
QLineEdit:focus {{
    border-color: {c['accent']};
}}
QLineEdit:hover {{
    border-color: {c['border_hover']};
}}

/* ── Комбобокс ── */
QComboBox {{
    background-color: {c['bg_input']};
    color: {c['text_primary']};
    border: 1px solid {c['border']};
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 13px;
    min-width: 120px;
}}
QComboBox:hover {{
    background-color: {c['bg_hover']};
    border-color: {c['border_hover']};
}}
QComboBox::drop-down {{
    border: none;
    width: 30px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {c['text_primary']};
    margin-right: 10px;
}}
QComboBox QAbstractItemView {{
    background-color: {c['bg_secondary']};
    color: {c['text_primary']};
    selection-background-color: {c['bg_hover']};
    border: 1px solid {c['border']};
    border-radius: 4px;
    outline: none;
}}

/* ── TextBrowser / TextEdit ── */
QTextBrowser, QTextEdit {{
    background-color: {c['news_bg']};
    color: {c['text_primary']};
    border: none;
    border-radius: 10px;
    selection-background-color: {c['accent']};
}}

/* ── Фреймы ── */
QFrame {{
    background-color: transparent;
}}

/* ── Скролл-области ── */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

/* ── Тулбар / заголовок ── */
QLabel {{
    background-color: transparent;
    color: {c['text_primary']};
}}

/* ── Прогресс-бар ── */
QProgressBar {{
    background-color: {c['bg_input']};
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background-color: {c['accent']};
    border-radius: 4px;
}}

/* ── Тулбар ── */
QToolTip {{
    background-color: {c['bg_secondary']};
    color: {c['text_primary']};
    border: 1px solid {c['border']};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}}
"""


class ThemeManager:
    """Менеджер тем приложения"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._current = "dark"
            cls._instance._listeners = []
        return cls._instance

    @property
    def current(self) -> str:
        return self._current

    @property
    def colors(self) -> dict:
        return LIGHT if self._current == "light" else DARK

    def is_light(self) -> bool:
        return self._current == "light"

    def add_listener(self, callback) -> None:
        """Подписаться на смену темы. callback() будет вызван после apply()."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback) -> None:
        """Отписаться от смены темы."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_listeners(self) -> None:
        """Уведомить всех слушателей о смене темы"""
        for callback in self._listeners:
            try:
                callback()
            except Exception as e:
                log_error(f"Ошибка при вызове слушателя темы: {e}")

    def apply(self, theme: str = None) -> None:
        """Применить тему ко всему приложению"""
        if theme:
            self._current = theme

        app = QApplication.instance()
        if not app:
            return

        c = self.colors
        app.setStyleSheet(_build_qss(c))

        # Обновляем QPalette для нативных диалогов
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window,          QColor(c["bg_main"]))
        palette.setColor(QPalette.ColorRole.WindowText,      QColor(c["text_primary"]))
        palette.setColor(QPalette.ColorRole.Base,            QColor(c["bg_secondary"]))
        palette.setColor(QPalette.ColorRole.AlternateBase,   QColor(c["bg_tertiary"]))
        palette.setColor(QPalette.ColorRole.Text,            QColor(c["text_primary"]))
        palette.setColor(QPalette.ColorRole.Button,          QColor(c["bg_button"]))
        palette.setColor(QPalette.ColorRole.ButtonText,      QColor(c["text_primary"]))
        palette.setColor(QPalette.ColorRole.Highlight,       QColor(c["accent"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(c["text_hint"]))
        app.setPalette(palette)

        log_info(f"Тема применена: {self._current}")
        
        # Уведомляем всех слушателей о смене темы
        log_info(f"Уведомление {len(self._listeners)} слушателей о смене темы")
        self._notify_listeners()

        # Уведомляем всех подписчиков
        dead = []
        for cb in self._listeners:
            try:
                cb()
            except Exception:
                dead.append(cb)
        for cb in dead:
            self._listeners.remove(cb)

    def toggle(self) -> str:
        """Переключить тему и вернуть новое значение"""
        self._current = "light" if self._current == "dark" else "dark"
        self.apply()
        return self._current

    def load_from_settings(self) -> None:
        """Загрузить тему из настроек"""
        from settings_manager import settings_manager
        theme = settings_manager.get_setting("theme", "dark")
        self.apply(theme)


# Глобальный синглтон
theme_manager = ThemeManager()


def get_tab_stylesheet() -> str:
    """Вернуть стиль для вкладок программ/драйверов"""
    c = theme_manager.colors
    return f"""
        QWidget {{
            background-color: {c['bg_main']};
            border-radius: 10px;
        }}
    """


def get_search_stylesheet() -> str:
    """Вернуть стиль для поля поиска"""
    c = theme_manager.colors
    return f"""
        QLineEdit {{
            background-color: {c['bg_input']};
            color: {c['text_primary']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
        }}
        QLineEdit:focus {{
            border: 1px solid {c['accent']};
        }}
        QLineEdit:hover {{
            border: 1px solid {c['border_hover']};
        }}
        QToolTip {{
            background-color: {c['bg_secondary']};
            color: {c['text_primary']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: 4px 8px;
        }}
    """


def get_card_stylesheet() -> str:
    """Вернуть стиль для карточек программ/драйверов"""
    c = theme_manager.colors
    return f"""
        QFrame {{
            background-color: {c['bg_card']};
            border: 1px solid {c['card_border']};
            border-radius: 12px;
        }}
        QFrame:hover {{
            background-color: {c['bg_hover']};
            border: 1px solid {c['border_hover']};
        }}
        QLabel {{
            color: {c['text_primary']};
            background-color: transparent;
            border: none;
        }}
    """


def colorize_pixmap(pixmap, color_str: str = None):
    """
    Перекрасить иконку (PNG с альфа-каналом) в нужный цвет.
    Сохраняет форму/прозрачность, меняет только цвет пикселей.
    
    Args:
        pixmap: QPixmap для перекраски
        color_str: hex-цвет вроде '#444444'. Если None — берёт text_primary из текущей темы.
    
    Returns:
        Новый QPixmap с применённым цветом
    """
    from PyQt6.QtGui import QPixmap, QPainter, QColor
    from PyQt6.QtCore import Qt

    if pixmap is None or pixmap.isNull():
        return pixmap

    if color_str is None:
        color_str = theme_manager.colors["text_primary"]

    result = QPixmap(pixmap.size())
    result.fill(Qt.GlobalColor.transparent)

    painter = QPainter(result)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    # Рисуем оригинал
    painter.drawPixmap(0, 0, pixmap)
    # Накладываем цвет поверх, сохраняя альфа-канал
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(result.rect(), QColor(color_str))
    painter.end()

    return result
