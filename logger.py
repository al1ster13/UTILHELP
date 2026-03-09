"""
Система логирования для UTILHELP - интегрированная с temp_manager
"""
import logging
import os
import sys
from datetime import datetime
from typing import Optional


class UtilhelpLogger:
    """Централизованная система логирования, использующая папку UTILHELPTEMP"""
    
    _instance: Optional['UtilhelpLogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is not None:
            return
            
        self._setup_logger()
    
    def _setup_logger(self):
        """Настройка логгера"""
        try:
            self._logger = logging.getLogger('UTILHELP')
            self._logger.setLevel(logging.INFO)
            
            # Получаем папку UTILHELPTEMP через temp_manager
            log_dir = self._get_utilhelptemp_directory()
            
            log_filename = f"utilhelp_{datetime.now().strftime('%Y%m%d')}.log"
            log_path = os.path.join(log_dir, log_filename)
            
            # Настраиваем форматтер
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s - %(module)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            # Файловый хендлер
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
            
            # Консольный хендлер (только для ошибок в debug режиме)
            if __debug__:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(logging.ERROR)
                console_handler.setFormatter(formatter)
                self._logger.addHandler(console_handler)
            
            # Логируем успешную инициализацию
            self._logger.info("=== UTILHELP Logger initialized ===")
            self._logger.info(f"Log file: {log_path}")
            self._logger.info(f"Log directory: {log_dir}")
            
        except Exception as e:
            print(f"Ошибка инициализации логгера: {e}")
            self._logger = logging.getLogger('UTILHELP')
            self._logger.setLevel(logging.ERROR)
            handler = logging.StreamHandler()
            self._logger.addHandler(handler)
    
    def _get_utilhelptemp_directory(self) -> str:
        """Получить папку UTILHELPTEMP (та же логика что в temp_manager)"""
        try:
            # Избегаем циклического импорта - используем прямую логику
            import tempfile
            system_temp = tempfile.gettempdir()
            
            for folder_name in ["UTILHELPTEMP", "UTILHELP", "UH"]:
                temp_dir = os.path.join(system_temp, folder_name)
                if os.path.exists(temp_dir) and os.access(temp_dir, os.W_OK):
                    return temp_dir
            
            utilhelptemp = os.path.join(system_temp, "UTILHELPTEMP")
            try:
                os.makedirs(utilhelptemp, exist_ok=True)
                if os.access(utilhelptemp, os.W_OK):
                    return utilhelptemp
            except:
                pass
            
            # Последний fallback
            return system_temp
            
        except Exception as e:
            print(f"Ошибка получения UTILHELPTEMP: {e}")
            # Последний fallback
            import tempfile
            return tempfile.gettempdir()
    
    def info(self, message: str):
        """Логирование информации"""
        if self._logger:
            self._logger.info(message)
    
    def warning(self, message: str):
        """Логирование предупреждения"""
        if self._logger:
            self._logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """Логирование ошибки"""
        if self._logger:
            self._logger.error(message, exc_info=exc_info)
    
    def debug(self, message: str):
        """Логирование отладочной информации"""
        if self._logger:
            self._logger.debug(message)
    
    def critical(self, message: str, exc_info: bool = False):
        """Логирование критической ошибки"""
        if self._logger:
            self._logger.critical(message, exc_info=exc_info)


# Глобальный экземпляр логгера
_logger_instance = None

def get_logger() -> UtilhelpLogger:
    """Получить экземпляр логгера"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = UtilhelpLogger()
    return _logger_instance


# Удобные функции для быстрого логирования (заменяют debug_log)
def log_info(message: str):
    """Быстрое логирование информации"""
    get_logger().info(message)

def log_warning(message: str):
    """Быстрое логирование предупреждения"""
    get_logger().warning(message)

def log_error(message: str, exc_info: bool = False):
    """Быстрое логирование ошибки"""
    get_logger().error(message, exc_info=exc_info)

def log_debug(message: str):
    """Быстрое логирование отладки"""
    get_logger().debug(message)

def log_critical(message: str, exc_info: bool = False):
    """Быстрое логирование критической ошибки"""
    get_logger().critical(message, exc_info=exc_info)


# Совместимость со старой системой debug_log
def debug_log(message: str):
    """Совместимость со старой системой debug_log - теперь использует новый логгер"""
    log_info(message)


def cleanup_old_logs():
    """Очистка старых логов в формате debug_log"""
    try:
        # Избегаем циклического импорта - используем прямую логику
        import tempfile
        system_temp = tempfile.gettempdir()
        
        # Ищем папку UTILHELPTEMP
        temp_dir = None
        for folder_name in ["UTILHELPTEMP", "UTILHELP", "UH"]:
            test_dir = os.path.join(system_temp, folder_name)
            if os.path.exists(test_dir):
                temp_dir = test_dir
                break
        
        if not temp_dir:
            return
        
        # Ищем старые логи в формате utilhelp_debug_*.log
        old_log_count = 0
        for filename in os.listdir(temp_dir):
            if filename.startswith('utilhelp_debug_') and filename.endswith('.log'):
                old_log_path = os.path.join(temp_dir, filename)
                try:
                    os.remove(old_log_path)
                    old_log_count += 1
                except Exception as e:
                    print(f"Не удалось удалить старый лог {filename}: {e}")
        
        if old_log_count > 0:
            log_info(f"Удалено {old_log_count} старых лог-файлов")
            
    except Exception as e:
        print(f"Ошибка очистки старых логов: {e}")


# Автоматически очищаем старые логи при импорте
try:
    cleanup_old_logs()
except:
    pass