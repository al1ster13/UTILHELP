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
        icon_path = get_icon_path(icon_name)
        
        if icon_path:
            pixmap = QPixmap(icon_path)
            
            if not pixmap.isNull() and size:
                scaled = pixmap.scaled(
                    size[0], size[1], 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                return scaled
            return pixmap
        
        return QPixmap()

    def create_icon_label(
        self, 
        icon_name: str, 
        size: Tuple[int, int] = (24, 24), 
        fallback_text: str = "•"
    ) -> QLabel:
        """Создать QLabel с иконкой и fallback текстом"""
        icon_label = QLabel()
        pixmap = self.load_icon_pixmap(icon_name, size)
        
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText(fallback_text)
            icon_label.setStyleSheet(f"font-size: {size[0]}px; color: #ffffff;")
        
        icon_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        icon_label.setContentsMargins(0, 2, 0, 0)
        return icon_label