"""
Миксин для работы с иконками
"""
from typing import Optional, Tuple
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from resource_path import get_icon_path


class IconMixin:
    """Миксин для работы с иконками"""

    def load_icon_pixmap(self, icon_name: str, size: Optional[Tuple[int, int]] = None) -> QPixmap:
        """Загрузить иконку с правильным путем для exe"""
        from theme_manager import theme_manager, colorize_pixmap

        icon_path = get_icon_path(icon_name)

        if icon_path:
            pixmap = QPixmap(icon_path)

            if not pixmap.isNull() and size:
                pixmap = pixmap.scaled(
                    size[0], size[1],
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

            if not pixmap.isNull() and theme_manager.is_light():
                pixmap = colorize_pixmap(pixmap, theme_manager.colors['text_secondary'])

            return pixmap

        return QPixmap()

    def create_icon_label(
        self,
        icon_name: str,
        size: Tuple[int, int] = (24, 24),
        fallback_text: str = "•"
    ) -> QLabel:
        from theme_manager import theme_manager

        icon_label = QLabel()
        pixmap = self.load_icon_pixmap(icon_name, size)

        if not pixmap.isNull():
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText(fallback_text)
            icon_label.setStyleSheet(f"font-size: {size[0]}px; color: {theme_manager.colors['text_primary']};")

        icon_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        icon_label.setContentsMargins(0, 2, 0, 0)
        return icon_label