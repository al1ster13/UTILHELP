import sys
import os

# Флаг использования Qt ресурсов
USE_QT_RESOURCES = True

try:
    import resources_rc
    USE_QT_RESOURCES = True
except ImportError:
    USE_QT_RESOURCES = False


def resource_path(relative_path):
    """Получить абсолютный путь к ресурсу, работает для dev и для PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def get_icon_path(icon_name):
    """Получить путь к системной иконке UTILHELP с поддержкой Qt ресурсов"""
    if USE_QT_RESOURCES:
        qrc_path = f":/icons/Icons/{icon_name}"
        from PyQt6.QtCore import QFile
        if QFile.exists(qrc_path):
            return qrc_path
    
    # Fallback на файловую систему (только для режима разработки)
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    
    search_paths = [
        os.path.join(exe_dir, 'Icons', icon_name),
    ]
    
    try:
        search_paths.append(resource_path(f"Icons/{icon_name}"))
    except:
        pass
    
    for path in search_paths:
        if path and os.path.exists(path):
            return path
    
    return None

def get_program_image_path(image_name):
    """Получить путь к картинке программы для скачивания с поддержкой Qt ресурсов"""
    if USE_QT_RESOURCES:
        qrc_path = f":/programs/ProgramImages/{image_name}"
        from PyQt6.QtCore import QFile
        if QFile.exists(qrc_path):
            return qrc_path
    
    if image_name and ('/' in image_name or '\\' in image_name):
        image_name = os.path.basename(image_name)
    
    if os.path.isabs(image_name) and os.path.exists(image_name):
        return image_name
    
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    
    search_paths = []
    
    if getattr(sys, 'frozen', False):
        search_paths.extend([
            os.path.join(exe_dir, 'assets', 'programs', image_name),
            os.path.join(exe_dir, 'ProgramImages', image_name),    # Fallback на старую структуру
            os.path.join(exe_dir, 'assets', 'icons', image_name),  # Fallback на системные иконки
        ])
    
    search_paths.extend([
        os.path.join(exe_dir, 'ProgramImages', image_name),
        os.path.join(exe_dir, 'Icons', image_name),  # Fallback на системные иконки
    ])
    
    try:
        search_paths.extend([
            resource_path(f"ProgramImages/{image_name}"),
            resource_path(f"assets/programs/{image_name}"),
            resource_path(f"Icons/{image_name}"),
            resource_path(f"assets/icons/{image_name}"),
        ])
    except:
        pass
    
    for path in search_paths:
        # try:
        #     from temp_manager import debug_log
        #     debug_log(f"Checking program image path: {path}")
        # except:
        #     pass
        
        if path and os.path.exists(path):
            # try:
            #     from temp_manager import debug_log
            #     debug_log(f"Found program image at: {path}")
            # except:
            #     pass
            return path
    
    # try:
    #     from temp_manager import debug_log
    #     debug_log(f"Program image not found: {image_name}. Checked paths: {search_paths}")
    # except:
    #     pass
    
    return None

def get_sound_path(sound_name):
    """Получить путь к звуковому файлу уведомления"""
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    
    search_paths = []
    
    # Приоритет 1: assets/sounds (извлеченные из QRC)
    search_paths.append(os.path.join(exe_dir, 'assets', 'sounds', sound_name))
    
    if getattr(sys, 'frozen', False):
        search_paths.extend([
            os.path.join(exe_dir, 'notification', sound_name),
        ])
    
    # Приоритет 2: notification (оригинальная папка для dev)
    search_paths.append(os.path.join(exe_dir, 'notification', sound_name))
    
    try:
        search_paths.extend([
            resource_path(f"assets/sounds/{sound_name}"),
            resource_path(f"notification/{sound_name}"),
        ])
    except:
        pass
    
    for path in search_paths:
        if path and os.path.exists(path):
            return path
    
    if USE_QT_RESOURCES:
        try:
            from resource_extractor import get_resource_extractor
            extractor = get_resource_extractor()
            output_path = os.path.join(extractor.sounds_dir, sound_name)
            qrc_path = f":/sounds/notification/{sound_name}"
            
            if extractor.extract_resource(qrc_path, output_path):
                return output_path
        except Exception:
            pass
    
    return None

def get_db_path(db_name):
    """Получить путь к базе данных"""
    exe_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    
    if getattr(sys, 'frozen', False):
        db_path = os.path.join(exe_dir, 'data', db_name)
        if os.path.exists(db_path):
            return db_path
        else:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            return db_path
    
    dev_path = os.path.join(exe_dir, db_name)
    if os.path.exists(dev_path):
        return dev_path
    
    try:
        fallback_path = resource_path(db_name)
        if os.path.exists(fallback_path):
            return fallback_path
    except:
        pass
    
    return db_name  