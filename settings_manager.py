import json
import os
from typing import Dict, Any
from datetime import datetime


def get_data_dir():
    """Получить папку для данных приложения"""
    import sys
    
    # Проверяем портативный режим
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    portable_marker = os.path.join(app_dir, "PORTABLE_MODE.txt")
    
    if os.path.exists(portable_marker):
        # Портативный режим - используем папку программы
        data_dir = os.path.join(app_dir, "data")
    else:
        # Обычный режим - используем AppData или папку программы
        try:
            # Пробуем использовать AppData
            appdata = os.environ.get('APPDATA')
            if appdata:
                utilhelp_data = os.path.join(appdata, 'UTILHELP')
                os.makedirs(utilhelp_data, exist_ok=True)
                # Проверяем права на запись
                test_file = os.path.join(utilhelp_data, 'test_write.tmp')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    data_dir = utilhelp_data
                except:
                    # Если AppData не работает, используем папку программы
                    data_dir = os.path.join(app_dir, "data")
            else:
                data_dir = os.path.join(app_dir, "data")
        except:
            data_dir = os.path.join(app_dir, "data")
    
    try:
        os.makedirs(data_dir, exist_ok=True)
        # Проверяем права на запись
        test_file = os.path.join(data_dir, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return data_dir
    except Exception as e:
        print(f"Ошибка создания папки данных: {e}")
        # В крайнем случае используем временную папку
        import tempfile
        temp_data = os.path.join(tempfile.gettempdir(), 'UTILHELP_data')
        os.makedirs(temp_data, exist_ok=True)
        return temp_data


class SettingsManager:
    """Менеджер настроек программы в JSON формате"""
    
    def __init__(self):
        self.data_dir = get_data_dir()
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        self.scan_cache_file = os.path.join(self.data_dir, "scan_cache.json")
        
        print(f"Используется папка данных: {self.data_dir}")
        
        self.default_settings = {
            "version": "1.0",
            "auto_scan_enabled": True,
            "scan_interval_minutes": 30,
            "cache_expiry_hours": 24,
            "last_scan_timestamp": None,
            "scan_on_startup": True,
            "notifications_enabled": True,
            "theme": "dark"
        }
        self.settings = self.load_settings()
        self.scan_cache = self.load_scan_cache()
    
    def load_settings(self) -> Dict[str, Any]:
        """Загрузка настроек из JSON файла"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    for key, value in self.default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
            else:
                return self.default_settings.copy()
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
            return self.default_settings.copy()
    
    def save_settings(self) -> bool:
        """Сохранение настроек в JSON файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
            return False
    
    def load_scan_cache(self) -> Dict[str, Any]:
        """Загрузка кеша сканирования"""
        try:
            if os.path.exists(self.scan_cache_file):
                with open(self.scan_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "last_scan": None,
                    "programs": {},
                    "drivers": {},
                    "scan_summary": {"programs_found": 0, "drivers_found": 0}
                }
        except Exception as e:
            print(f"Ошибка загрузки кеша сканирования: {e}")
            return {
                "last_scan": None,
                "programs": {},
                "drivers": {},
                "scan_summary": {"programs_found": 0, "drivers_found": 0}
            }
    
    def save_scan_cache(self, programs_status: Dict, drivers_status: Dict, scan_summary: Dict) -> bool:
        """Сохранение результатов сканирования в кеш"""
        try:
            cache_data = {
                "last_scan": datetime.now().isoformat(),
                "programs": programs_status,
                "drivers": drivers_status,
                "scan_summary": scan_summary
            }
            
            with open(self.scan_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            self.settings["last_scan_timestamp"] = cache_data["last_scan"]
            self.save_settings()
            
            return True
        except Exception as e:
            print(f"Ошибка сохранения кеша сканирования: {e}")
            return False
    
    def is_cache_valid(self) -> bool:
        """Проверка актуальности кеша"""
        if not self.scan_cache.get("last_scan"):
            return False
        
        try:
            last_scan = datetime.fromisoformat(self.scan_cache["last_scan"])
            now = datetime.now()
            hours_passed = (now - last_scan).total_seconds() / 3600
            
            return hours_passed < self.settings.get("cache_expiry_hours", 24)
        except Exception:
            return False
    
    def get_setting(self, key: str, default=None):
        """Получение значения настройки"""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Установка значения настройки"""
        self.settings[key] = value
        return self.save_settings()
    
    def get_cached_status(self, item_name: str, item_type: str) -> Dict[str, Any]:
        """Получение статуса из кеша"""
        if not self.is_cache_valid():
            return {"installed": False, "exact_name": None, "version": None}
        
        cache_key = "programs" if item_type == "programs" else "drivers"
        return self.scan_cache.get(cache_key, {}).get(item_name, {"installed": False, "exact_name": None, "version": None})
    
    def should_auto_scan(self) -> bool:
        """Проверка нужно ли выполнять автоматическое сканирование"""
        if not self.settings.get("auto_scan_enabled", True):
            return False
        
        if not self.is_cache_valid():
            return True
        
        if not self.settings.get("last_scan_timestamp"):
            return True
        
        try:
            last_scan = datetime.fromisoformat(self.settings["last_scan_timestamp"])
            now = datetime.now()
            minutes_passed = (now - last_scan).total_seconds() / 60
            
            return minutes_passed >= self.settings.get("scan_interval_minutes", 30)
        except Exception:
            return True
    
    def migrate_from_db(self):
        """Миграция настроек из старой SQLite базы (если есть)"""
        try:
            # Проверяем старые пути
            old_paths = [
                "settings.db",
                os.path.join("data", "settings.db"),
                os.path.join(self.data_dir, "settings.db")
            ]
            
            for old_db_path in old_paths:
                if os.path.exists(old_db_path):
                    print(f"Найдена старая база настроек: {old_db_path}")
                    backup_path = os.path.join(self.data_dir, "settings.db.backup")
                    if not os.path.exists(backup_path):
                        try:
                            if old_db_path != backup_path:
                                os.rename(old_db_path, backup_path)
                                print(f"Старая база перенесена в {backup_path}")
                        except Exception as e:
                            print(f"Ошибка переноса базы: {e}")
                            
        except Exception as e:
            print(f"Ошибка миграции: {e}")

settings_manager = SettingsManager()