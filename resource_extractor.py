"""
Извлечение ресурсов из Qt Resource System в файловую систему
"""
import os
import sys
from PyQt6.QtCore import QFile, QIODevice
from logger import log_info, log_error, log_debug


class ResourceExtractor:
    """Класс для извлечения ресурсов из QRC в файловую систему"""
    
    def __init__(self):
        self.app_dir = self._get_app_dir()
        self.assets_dir = os.path.join(self.app_dir, "assets")
        self.sounds_dir = os.path.join(self.assets_dir, "sounds")
        self.icons_dir = os.path.join(self.assets_dir, "icons")
    
    def _get_app_dir(self):
        """Получить директорию приложения"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))
    
    def ensure_directories(self):
        """Создать необходимые директории"""
        try:
            os.makedirs(self.sounds_dir, exist_ok=True)
            log_debug(f"Directories created: {self.sounds_dir}")
            return True
        except Exception as e:
            log_error(f"Failed to create directories: {e}")
            return False
    
    def extract_resource(self, qrc_path, output_path):
        """
        Извлечь ресурс из QRC в файл
        
        Args:
            qrc_path: Путь к ресурсу в QRC (например, ":/sounds/notification/file.wav")
            output_path: Путь для сохранения файла
        
        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            if not QFile.exists(qrc_path):
                log_error(f"Resource not found in QRC: {qrc_path}")
                return False
            
            # Открываем ресурс
            qrc_file = QFile(qrc_path)
            if not qrc_file.open(QIODevice.OpenModeFlag.ReadOnly):
                log_error(f"Failed to open QRC resource: {qrc_path}")
                return False
            
            # Читаем данные
            data = qrc_file.readAll()
            qrc_file.close()
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Записываем в файл
            with open(output_path, 'wb') as f:
                f.write(data.data())
            
            log_debug(f"Extracted: {qrc_path} -> {output_path}")
            return True
            
        except Exception as e:
            log_error(f"Failed to extract resource {qrc_path}: {e}")
            return False
    
    def extract_sounds(self):
        """Извлечь все звуки из QRC в assets/sounds"""
        sounds = [
            "utilhelp-notification.wav",
            "utilhelp-notification-error.wav"
        ]
        
        success_count = 0
        for sound_name in sounds:
            qrc_path = f":/sounds/notification/{sound_name}"
            output_path = os.path.join(self.sounds_dir, sound_name)
            
            # Извлекаем только если файл не существует или устарел
            if not os.path.exists(output_path) or self._should_update(qrc_path, output_path):
                if self.extract_resource(qrc_path, output_path):
                    success_count += 1
                    log_info(f"Sound extracted: {sound_name}")
            else:
                success_count += 1
                log_debug(f"Sound already exists: {sound_name}")
        
        log_info(f"Sounds extraction: {success_count}/{len(sounds)} successful")
        return success_count == len(sounds)
    
    def extract_icons(self, icon_names=None):
        """
        Извлечь иконки из QRC в assets/icons
        
        Args:
            icon_names: Список имен иконок для извлечения. Если None, извлекаются все системные иконки.
        """
        if icon_names is None:
            # Все системные иконки для извлечения в файловую систему
            icon_names = [
                "books.png",
                "box.png",
                "button download.png",
                "calendar.png",
                "cancel.png",
                "closemenu.png",
                "complete.png",
                "completenotif.png",
                "contacts.png",
                "delete.png",
                "deletelibrary.png",
                "email.png",
                "error.png",
                "errornotif.png",
                "fallbackbox.png",
                "file.png",
                "filesize.png",
                "github.png",
                "info.png",
                "infologo.png",
                "installed.png",
                "installer.png",
                "installer2.png",
                "interface.png",
                "logo64x64.png",
                "minimizemenu.png",
                "opensize.png",
                "preparation.png",
                "settings.png",
                "snowflake.png",
                "speed.png",
                "telegram.png",
                "tempfile.png",
                "time.png",
                "unwrapmenu.png",
                "update.png",
                "updatenotif.png",
                "updatetab.png",
                "utilhelp.ico",
                "utilhelp14x14.png",
                "utilhelplogo24.png",
                "whitetheme.png",
            ]
        
        success_count = 0
        for icon_name in icon_names:
            qrc_path = f":/icons/Icons/{icon_name}"
            output_path = os.path.join(self.icons_dir, icon_name)
            
            if not os.path.exists(output_path) or self._should_update(qrc_path, output_path):
                if self.extract_resource(qrc_path, output_path):
                    success_count += 1
                    log_debug(f"Icon extracted: {icon_name}")
            else:
                success_count += 1
                log_debug(f"Icon already exists: {icon_name}")
        
        log_info(f"Icons extraction: {success_count}/{len(icon_names)} successful")
        return success_count == len(icon_names)
    
    def _should_update(self, qrc_path, file_path):
        """
        Проверить, нужно ли обновить файл
        
        Args:
            qrc_path: Путь к ресурсу в QRC
            file_path: Путь к файлу на диске
        
        Returns:
            bool: True если нужно обновить
        """
        try:
            if not os.path.exists(file_path):
                return True
            
            # Сравниваем размеры
            qrc_file = QFile(qrc_path)
            if qrc_file.open(QIODevice.OpenModeFlag.ReadOnly):
                qrc_size = qrc_file.size()
                qrc_file.close()
                
                file_size = os.path.getsize(file_path)
                
                if qrc_size != file_size:
                    log_debug(f"Size mismatch: QRC={qrc_size}, File={file_size}")
                    return True
            
            return False
            
        except Exception as e:
            log_error(f"Error checking file update: {e}")
            return True
    
    def extract_all(self):
        """Извлечь все необходимые ресурсы"""
        log_info("Starting resource extraction...")
        
        if not self.ensure_directories():
            log_error("Failed to create directories")
            return False
        
        # Извлекаем только звуки (иконки работают напрямую из QRC)
        sounds_ok = self.extract_sounds()
        
        if sounds_ok:
            log_info("✅ All resources extracted successfully")
            return True
        else:
            log_error("❌ Some resources failed to extract")
            return False


# Глобальный экземпляр
_extractor = None


def get_resource_extractor():
    """Получить глобальный экземпляр экстрактора"""
    global _extractor
    if _extractor is None:
        _extractor = ResourceExtractor()
    return _extractor


def extract_resources_on_startup():
    """
    Извлечь ресурсы при запуске программы
    Вызывать в main.py после импорта resources_rc
    """
    try:
        import resources_rc
        extractor = get_resource_extractor()
        return extractor.extract_all()
    except ImportError:
        log_debug("Qt resources not available, skipping extraction")
        return False
