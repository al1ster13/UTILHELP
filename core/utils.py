"""
Утилиты для UTILHELP
"""
from typing import Optional, Tuple, Dict, Any
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from resource_path import get_icon_path
from .types import StyleSheet


class StyleSheets:
    """Коллекция стилей для переиспользования"""
    
    # Основные цвета
    COLORS = {
        'background_primary': '#1a1a1a',
        'background_secondary': '#2d2d2d',
        'background_tertiary': '#3d3d3d',
        'text_primary': '#ffffff',
        'text_secondary': '#cccccc',
        'text_muted': '#888888',
        'accent': '#4CAF50',
        'border': '#3d3d3d',
        'hover': '#4d4d4d'
    }
    
    @staticmethod
    def get_base_widget_style() -> StyleSheet:
        """Базовый стиль для виджетов"""
        return f"""
            QWidget {{
                background-color: {StyleSheets.COLORS['background_primary']};
                color: {StyleSheets.COLORS['text_primary']};
                font-family: 'Segoe UI', Arial, sans-serif;
                border-radius: 8px;
            }}
        """
    
    @staticmethod
    def get_button_style(active: bool = False) -> StyleSheet:
        """Стиль для кнопок"""
        bg_color = StyleSheets.COLORS['background_tertiary'] if active else 'transparent'
        text_color = StyleSheets.COLORS['text_primary'] if active else StyleSheets.COLORS['text_secondary']
        
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: normal;
                padding: 8px 16px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {StyleSheets.COLORS['background_secondary']};
                color: {StyleSheets.COLORS['text_primary']};
            }}
            QPushButton:focus {{
                outline: none;
                border: none;
            }}
        """
    
    @staticmethod
    def get_title_style(size: int = 24) -> StyleSheet:
        """Стиль для заголовков"""
        return f"""
            QLabel {{
                color: {StyleSheets.COLORS['text_primary']};
                font-size: {size}px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """
    
    @staticmethod
    def get_description_style() -> StyleSheet:
        """Стиль для описаний"""
        return f"""
            QLabel {{
                color: {StyleSheets.COLORS['text_secondary']};
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """
    
    @staticmethod
    def get_setting_item_style() -> StyleSheet:
        """Стиль для элементов настроек"""
        return f"""
            QWidget {{
                background-color: {StyleSheets.COLORS['background_secondary']};
                border-radius: 12px;
                border: 1px solid {StyleSheets.COLORS['border']};
            }}
            QWidget:hover {{
                border: 1px solid {StyleSheets.COLORS['hover']};
                background-color: #333333;
            }}
        """


class WidgetFactory:
    """Фабрика для создания стандартных виджетов"""
    
    @staticmethod
    def create_icon_label(
        icon_name: str, 
        size: Tuple[int, int] = (24, 24), 
        fallback_text: str = "•"
    ) -> QLabel:
        """Создать QLabel с иконкой"""
        icon_label = QLabel()
        
        icon_path = get_icon_path(icon_name)
        if icon_path:
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    size[0], size[1], 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                icon_label.setPixmap(scaled)
            else:
                icon_label.setText(fallback_text)
                icon_label.setStyleSheet(f"font-size: {size[0]}px; color: #ffffff;")
        else:
            icon_label.setText(fallback_text)
            icon_label.setStyleSheet(f"font-size: {size[0]}px; color: #ffffff;")
        
        icon_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        icon_label.setContentsMargins(0, 2, 0, 0)
        return icon_label
    
    @staticmethod
    def create_title_label(text: str, size: int = 24) -> QLabel:
        """Создать заголовок"""
        label = QLabel(text)
        label.setStyleSheet(StyleSheets.get_title_style(size))
        label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        return label
    
    @staticmethod
    def create_description_label(text: str, word_wrap: bool = True) -> QLabel:
        """Создать описание"""
        label = QLabel(text)
        label.setStyleSheet(StyleSheets.get_description_style())
        label.setWordWrap(word_wrap)
        return label
    
    @staticmethod
    def create_section_title(icon_name: str, title: str) -> QWidget:
        """Создать заголовок секции с иконкой"""
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        title_layout.setContentsMargins(0, 0, 0, 20)
        
        icon_label = WidgetFactory.create_icon_label(icon_name, (24, 24))
        icon_label.setContentsMargins(0, 4, 0, 0)
        title_layout.addWidget(icon_label)
        
        title_text = WidgetFactory.create_title_label(title)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        
        title_container = QWidget()
        title_container.setLayout(title_layout)
        return title_container
    
    @staticmethod
    def create_control_button(
        icon_name: str, 
        tooltip: str, 
        size: Tuple[int, int] = (24, 24)
    ) -> QPushButton:
        """Создать кнопку управления"""
        btn = QPushButton()
        btn.setFixedSize(size[0], size[1])
        btn.setToolTip(tooltip)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:pressed {
                background-color: #4d4d4d;
            }
        """)
        
        icon_path = get_icon_path(icon_name)
        if icon_path:
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                icon_size = (size[0] - 8, size[1] - 8)  # Немного меньше кнопки
                scaled = pixmap.scaled(
                    icon_size[0], icon_size[1],
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                btn.setIcon(QIcon(scaled))
        
        return btn


class LayoutUtils:
    """Утилиты для работы с layout'ами"""
    
    @staticmethod
    def clear_layout(layout) -> None:
        """Очистить layout от всех виджетов"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    @staticmethod
    def create_horizontal_layout(
        margins: Tuple[int, int, int, int] = (0, 0, 0, 0),
        spacing: int = 0
    ) -> QHBoxLayout:
        """Создать горизонтальный layout"""
        layout = QHBoxLayout()
        layout.setContentsMargins(*margins)
        layout.setSpacing(spacing)
        return layout
    
    @staticmethod
    def create_vertical_layout(
        margins: Tuple[int, int, int, int] = (0, 0, 0, 0),
        spacing: int = 0
    ) -> QVBoxLayout:
        """Создать вертикальный layout"""
        layout = QVBoxLayout()
        layout.setContentsMargins(*margins)
        layout.setSpacing(spacing)
        return layout


class ValidationUtils:
    """Утилиты для валидации данных"""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Проверить валидность URL"""
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Проверить валидность email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Очистить имя файла от недопустимых символов"""
        import re
        # Удаляем недопустимые символы
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Ограничиваем длину
        if len(sanitized) > 100:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            sanitized = name[:90] + ('.' + ext if ext else '')
        return sanitized


class FormatUtils:
    """Утилиты для форматирования данных"""
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Форматировать размер файла"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Форматировать продолжительность"""
        if seconds < 60:
            return f"{seconds}с"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}м {seconds % 60}с"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}ч {minutes}м"
    
    @staticmethod
    def format_speed(bytes_per_second: float) -> str:
        """Форматировать скорость загрузки"""
        if bytes_per_second < 1024:
            return f"{bytes_per_second:.1f} B/s"
        elif bytes_per_second < 1024 * 1024:
            return f"{bytes_per_second / 1024:.1f} KB/s"
        else:
            return f"{bytes_per_second / (1024 * 1024):.1f} MB/s"