from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


def load_program_image(image_name, callback=None):
    """
    Загрузить изображение программы/драйвера
    
    Args:
        image_name: Имя файла изображения
        callback: Опциональная функция обратного вызова (logo_name, pixmap) для асинхронной загрузки
        
    Returns:
        QPixmap если изображение в кэше, иначе None (будет загружено асинхронно если указан callback)
    """
    if not image_name:
        return None
    
    from logo_manager import get_logo_manager
    logo_manager = get_logo_manager()
    
    return logo_manager.load_logo(image_name, callback)


def create_program_icon(image_name, size=(24, 24)):
    """Создать иконку для кнопки из изображения программы"""
    from PyQt6.QtGui import QIcon
    
    pixmap = load_program_image(image_name)
    
    if not pixmap or pixmap.isNull():
        return None
    
    scaled_pixmap = pixmap.scaled(
        size[0], size[1], 
        Qt.AspectRatioMode.KeepAspectRatio, 
        Qt.TransformationMode.SmoothTransformation
    )
    
    return QIcon(scaled_pixmap)