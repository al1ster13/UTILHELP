"""
Менеджер для загрузки и кэширования логотипов программ и драйверов с GitHub
"""
import os
import requests
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QThread, pyqtSignal
from settings_manager import get_data_dir
from logger import log_info, log_error, log_debug


GITHUB_LOGOS_URL = "https://al1ster13.github.io/utilhelp-data/logos/"


def get_logos_cache_dir():
    """Получить папку для кэша логотипов"""
    data_dir = get_data_dir()
    logos_cache_dir = os.path.join(data_dir, "data", "cache", "logos")
    
    try:
        os.makedirs(logos_cache_dir, exist_ok=True)
        log_debug(f"Папка кэша логотипов: {logos_cache_dir}")
        return logos_cache_dir
    except Exception as e:
        log_error(f"Ошибка создания папки кэша логотипов: {e}")
        # Используем временную папку
        import tempfile
        temp_cache = os.path.join(tempfile.gettempdir(), 'UTILHELP_cache', 'logos')
        os.makedirs(temp_cache, exist_ok=True)
        log_info(f"Используется временная папка для кэша логотипов: {temp_cache}")
        return temp_cache


class LogoDownloader(QThread):
    """Загрузчик логотипов с GitHub"""
    download_completed = pyqtSignal(str, str)  
    download_failed = pyqtSignal(str)  
    
    def __init__(self, logo_name):
        super().__init__()
        self.logo_name = logo_name
        self.cache_dir = get_logos_cache_dir()
    
    def run(self):
        """Загрузка логотипа"""
        try:
            if not self.logo_name:
                log_error("Попытка загрузить логотип с пустым именем")
                self.download_failed.emit(self.logo_name)
                return
            
            cache_path = os.path.join(self.cache_dir, self.logo_name)
            if os.path.exists(cache_path):
                log_debug(f"Логотип {self.logo_name} найден в кэше: {cache_path}")
                self.download_completed.emit(self.logo_name, cache_path)
                return
            
            url = f"{GITHUB_LOGOS_URL}{self.logo_name}"
            log_info(f"Загрузка логотипа {self.logo_name} с {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                with open(cache_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                log_info(f"✓ Логотип {self.logo_name} успешно загружен ({file_size} байт) и сохранён в {cache_path}")
                self.download_completed.emit(self.logo_name, cache_path)
            else:
                log_error(f"Не удалось загрузить логотип {self.logo_name}: HTTP {response.status_code}")
                self.download_failed.emit(self.logo_name)
                
        except requests.Timeout:
            log_error(f"Таймаут при загрузке логотипа {self.logo_name}")
            self.download_failed.emit(self.logo_name)
        except requests.RequestException as e:
            log_error(f"Ошибка сети при загрузке логотипа {self.logo_name}: {e}")
            self.download_failed.emit(self.logo_name)
        except Exception as e:
            log_error(f"Неожиданная ошибка при загрузке логотипа {self.logo_name}: {e}")
            import traceback
            traceback.print_exc()
            self.download_failed.emit(self.logo_name)


class LogoManager:
    """Менеджер для работы с логотипами"""
    def __init__(self):
        self.cache_dir = get_logos_cache_dir()
        self.active_downloads = {}  
        self.callbacks = {}  
    
    def get_logo_path(self, logo_name):
        """
        Получить путь к логотипу (из кэша или локальной папки)
        
        Args:
            logo_name: Имя файла логотипа
            
        Returns:
            Путь к файлу логотипа или None
        """
        if not logo_name:
            return None
        
        cache_path = os.path.join(self.cache_dir, logo_name)
        if os.path.exists(cache_path):
            log_debug(f"Логотип {logo_name} найден в кэше")
            return cache_path
        
        from resource_path import get_program_image_path
        local_path = get_program_image_path(logo_name)
        if local_path and os.path.exists(local_path):
            log_debug(f"Логотип {logo_name} найден локально: {local_path}")
            return local_path
        
        log_debug(f"Логотип {logo_name} не найден ни в кэше, ни локально")
        return None
    
    def get_cached_logo_path(self, logo_name):
        """
        Алиас для get_logo_path для обратной совместимости
        
        Args:
            logo_name: Имя файла логотипа
            
        Returns:
            Путь к файлу логотипа или None
        """
        return self.get_logo_path(logo_name)
    
    def load_logo(self, logo_name, callback=None):
        """
        Загрузить логотип (синхронно из кэша или асинхронно с GitHub)
        
        Args:
            logo_name: Имя файла логотипа
            callback: Функция обратного вызова (logo_name, pixmap)
            
        Returns:
            QPixmap если логотип в кэше, иначе None (будет загружен асинхронно)
        """
        if not logo_name:
            return None
        
        logo_path = self.get_logo_path(logo_name)
        if logo_path:
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                log_debug(f"Логотип {logo_name} успешно загружен из {logo_path}")
                return pixmap
            else:
                log_error(f"Не удалось создать QPixmap из {logo_path}")
        
        if callback:
            log_info(f"Запуск асинхронной загрузки логотипа {logo_name}")
            self.download_logo_async(logo_name, callback)
        
        return None
    
    def download_logo_async(self, logo_name, callback):
        """
        Загрузить логотип асинхронно с GitHub
        
        Args:
            logo_name: Имя файла логотипа
            callback: Функция обратного вызова (logo_name, pixmap)
        """
        if not logo_name:
            return
        
        if logo_name not in self.callbacks:
            self.callbacks[logo_name] = []
        self.callbacks[logo_name].append(callback)
        
        if logo_name in self.active_downloads:
            log_debug(f"Логотип {logo_name} уже загружается, добавлен callback")
            return
        
        log_info(f"Создание загрузчика для логотипа {logo_name}")
        downloader = LogoDownloader(logo_name)
        downloader.download_completed.connect(self._on_download_completed)
        downloader.download_failed.connect(self._on_download_failed)
        
        self.active_downloads[logo_name] = downloader
        downloader.start()
    
    def _on_download_completed(self, logo_name, file_path):
        """Обработка успешной загрузки"""
        log_info(f"Обработка успешной загрузки логотипа {logo_name}")
        
        if logo_name in self.active_downloads:
            del self.active_downloads[logo_name]
        
        pixmap = QPixmap(file_path)
        
        if pixmap.isNull():
            log_error(f"Не удалось создать QPixmap из загруженного файла {file_path}")
        
        if logo_name in self.callbacks:
            callback_count = len(self.callbacks[logo_name])
            log_debug(f"Вызов {callback_count} callback(s) для логотипа {logo_name}")
            
            for callback in self.callbacks[logo_name]:
                try:
                    callback(logo_name, pixmap)
                except Exception as e:
                    log_error(f"Ошибка в callback для {logo_name}: {e}")
                    import traceback
                    traceback.print_exc()
            
            del self.callbacks[logo_name]
    
    def _on_download_failed(self, logo_name):
        """Обработка ошибки загрузки"""
        log_error(f"Обработка ошибки загрузки логотипа {logo_name}")
        
        if logo_name in self.active_downloads:
            del self.active_downloads[logo_name]
        
        if logo_name in self.callbacks:
            callback_count = len(self.callbacks[logo_name])
            log_debug(f"Вызов {callback_count} callback(s) с None для логотипа {logo_name}")
            
            for callback in self.callbacks[logo_name]:
                try:
                    callback(logo_name, None)
                except Exception as e:
                    log_error(f"Ошибка в callback для {logo_name}: {e}")
                    import traceback
                    traceback.print_exc()
            
            del self.callbacks[logo_name]
    
    def clear_cache(self):
        """Очистить кэш логотипов"""
        try:
            import shutil
            if os.path.exists(self.cache_dir):
                file_count = len([f for f in os.listdir(self.cache_dir) if os.path.isfile(os.path.join(self.cache_dir, f))])
                shutil.rmtree(self.cache_dir)
                os.makedirs(self.cache_dir, exist_ok=True)
                log_info(f"✓ Кэш логотипов очищен ({file_count} файлов удалено)")
            else:
                log_info("Кэш логотипов уже пуст")
        except Exception as e:
            log_error(f"Ошибка очистки кэша логотипов: {e}")
            import traceback
            traceback.print_exc()
    
    def cleanup(self):
        """Очистка ресурсов и завершение всех потоков"""
        log_info("Очистка менеджера логотипов...")
        
        for logo_name, downloader in list(self.active_downloads.items()):
            try:
                if downloader.isRunning():
                    log_debug(f"Ожидание завершения загрузки: {logo_name}")
                    downloader.quit()
                    downloader.wait(1000)  
                    if downloader.isRunning():
                        downloader.terminate()
                        downloader.wait()
            except Exception as e:
                log_error(f"Ошибка при остановке загрузчика {logo_name}: {e}")
        
        self.active_downloads.clear()
        self.callbacks.clear()
        log_info("Менеджер логотипов очищен")


_logo_manager = None

def get_logo_manager():
    """Получить глобальный экземпляр менеджера логотипов"""
    global _logo_manager
    if _logo_manager is None:
        log_info("Инициализация менеджера логотипов")
        _logo_manager = LogoManager()
    return _logo_manager

def cleanup_logo_manager():
    """Очистить менеджер логотипов при выходе из приложения"""
    global _logo_manager
    if _logo_manager is not None:
        _logo_manager.cleanup()
        _logo_manager = None
