import requests
import json
import os
from datetime import datetime, timedelta
from PyQt6.QtCore import QThread, pyqtSignal


GITHUB_PAGES_URL = "https://al1ster13.github.io/utilhelp-data/"
CACHE_DURATION = timedelta(hours=1)  


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
        return app_dir
    else:
        # Обычный режим - используем AppData или текущую папку
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
                    return utilhelp_data
                except:
                    pass
            
            # Если AppData не работает, используем папку программы
            return app_dir
            
        except:
            # В крайнем случае используем папку программы
            return app_dir


def get_cache_dir():
    """Получить папку для кэша"""
    data_dir = get_data_dir()
    cache_dir = os.path.join(data_dir, "cache")
    
    try:
        os.makedirs(cache_dir, exist_ok=True)
        # Проверяем права на запись
        test_file = os.path.join(cache_dir, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return cache_dir
    except Exception as e:
        print(f"Ошибка создания папки кэша: {e}")
        # Используем временную папку
        import tempfile
        temp_cache = os.path.join(tempfile.gettempdir(), 'UTILHELP_cache')
        os.makedirs(temp_cache, exist_ok=True)
        return temp_cache  


class DataLoader(QThread):
    """Загрузчик данных с GitHub Pages"""
    loading_started = pyqtSignal()
    loading_progress = pyqtSignal(str, int)  
    loading_completed = pyqtSignal(dict)  
    loading_failed = pyqtSignal(str)  
    
    def __init__(self):
        super().__init__()
        self.data = {
            'programs': [],
            'drivers': [],
            'news': []
        }
        
        # Получаем безопасную папку для кэша
        self.cache_dir = get_cache_dir()
        print(f"Используется папка кэша: {self.cache_dir}")
    
    def run(self):
        """Загрузка данных"""
        self.loading_started.emit()
        
        try:
            self.loading_progress.emit("Подключение к серверу", 10)
            
            self.loading_progress.emit("Загрузка программ", 30)
            programs_data = self.download_json('programs')
            if programs_data:
                self.data['programs'] = programs_data.get('programs', [])
                self.save_to_cache('programs', programs_data)
            else:
                raise Exception("Не удалось загрузить данные программ")
            
            self.loading_progress.emit("Загрузка драйверов", 60)
            drivers_data = self.download_json('drivers')
            if drivers_data:
                self.data['drivers'] = drivers_data.get('drivers', [])
                self.save_to_cache('drivers', drivers_data)
            else:
                raise Exception("Не удалось загрузить данные драйверов")
            
            self.loading_progress.emit("Загрузка новостей", 90)
            news_data = self.download_json('news')
            if news_data:
                self.data['news'] = news_data.get('news', [])
                self.save_to_cache('news', news_data)
            else:
                raise Exception("Не удалось загрузить данные новостей")
            
            self.loading_progress.emit("Готово", 100)
            self.loading_completed.emit(self.data)
            
        except Exception as e:
            print(f"Ошибка загрузки с GitHub: {e}")
            import traceback
            traceback.print_exc()
            
            if self.load_from_cache():
                print("✓ Данные загружены из кэша (резервная копия)")
                self.loading_completed.emit(self.data)
            else:
                self.loading_failed.emit(f"Ошибка загрузки данных: {str(e)}")
    
    def download_json(self, data_type):
        """Скачивает JSON файл с GitHub"""
        try:
            url = f"{GITHUB_PAGES_URL}{data_type}.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"HTTP {response.status_code}")
                
        except requests.RequestException as e:
            raise Exception(f"Нет подключения к интернету")
        except json.JSONDecodeError as e:
            raise Exception(f"Ошибка формата данных")
    
    def load_from_cache(self):
        """Загружает данные из кэша если они свежие"""
        try:
            cache_time_file = os.path.join(self.cache_dir, "cache_time.txt")
            
            if os.path.exists(cache_time_file):
                with open(cache_time_file, 'r') as f:
                    cache_time = datetime.fromisoformat(f.read().strip())
                    
                if datetime.now() - cache_time < CACHE_DURATION:
                    for data_type in ['programs', 'drivers', 'news']:
                        cache_file = os.path.join(self.cache_dir, f"{data_type}.json")
                        if os.path.exists(cache_file):
                            with open(cache_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                self.data[data_type] = data.get(data_type, [])
                    
                    print("✓ Данные загружены из кэша")
                    return True
            
            return False
            
        except Exception as e:
            print(f"Ошибка загрузки кэша: {e}")
            return False
    
    def save_to_cache(self, data_type, data):
        """Сохраняет данные в кэш"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{data_type}.json")
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            cache_time_file = os.path.join(self.cache_dir, "cache_time.txt")
            with open(cache_time_file, 'w') as f:
                f.write(datetime.now().isoformat())
                
        except Exception as e:
            print(f"Ошибка сохранения кэша: {e}")


class JsonDataManager:
    """Менеджер для работы с JSON данными"""
    def __init__(self):
        self.loader = None
        self.is_loading = False
        self.data = {
            'programs': [],
            'drivers': [],
            'news': []
        }
    
    def load_data(self, on_complete=None, on_failed=None, on_progress=None):
        """Загружает данные с GitHub"""
        if self.is_loading:
            return
        
        self.is_loading = True
        
        if hasattr(self, 'loader') and self.loader is not None:
            try:
                if self.loader.isRunning():
                    self.loader.quit()
                    self.loader.wait()
            except:
                pass
        
        self.loader = DataLoader()
        
        if on_complete:
            self.loader.loading_completed.connect(lambda data: self._on_complete(data, on_complete))
        
        if on_failed:
            self.loader.loading_failed.connect(lambda error: self._on_failed(error, on_failed))
        
        if on_progress:
            self.loader.loading_progress.connect(on_progress)
        
        self.loader.start()
    
    def _on_complete(self, data, callback):
        """Обработка успешной загрузки"""
        self.is_loading = False
        self.data = data
        callback(data)
    
    def _on_failed(self, error, callback):
        """Обработка ошибки загрузки"""
        self.is_loading = False
        callback(error)
    
    def get_programs(self):
        """Получить список программ"""
        return self.data.get('programs', [])
    
    def get_drivers(self):
        """Получить список драйверов"""
        return self.data.get('drivers', [])
    
    def get_news(self):
        """Получить список новостей"""
        return self.data.get('news', [])
    
    def search_programs(self, query):
        """Поиск программ"""
        if not query:
            return self.get_programs()
        
        query = query.lower()
        results = []
        
        for program in self.get_programs():
            name = program.get('name', '').lower()
            description = program.get('description', '').lower()
            
            if query in name or query in description:
                results.append(program)
        
        return results
    
    def search_drivers(self, query):
        """Поиск драйверов"""
        if not query:
            return self.get_drivers()
        
        query = query.lower()
        results = []
        
        for driver in self.get_drivers():
            name = driver.get('name', '').lower()
            description = driver.get('description', '').lower()
            
            if query in name or query in description:
                results.append(driver)
        
        return results
    
    def get_programs_by_category(self, category):
        """Получить программы по категории"""
        if not category:
            return self.get_programs()
        
        results = []
        for program in self.get_programs():
            if program.get('category') == category:
                results.append(program)
        
        return results
    
    def get_drivers_by_category(self, category):
        """Получить драйверы по категории"""
        if not category:
            return self.get_drivers()
        
        results = []
        for driver in self.get_drivers():
            if driver.get('category') == category:
                results.append(driver)
        
        return results
    
    def clear_cache(self):
        """Очистить кэш"""
        try:
            cache_dir = get_cache_dir()
            cache_files = ['programs.json', 'drivers.json', 'news.json', 'cache_time.txt']
            for filename in cache_files:
                cache_file = os.path.join(cache_dir, filename)
                if os.path.exists(cache_file):
                    os.remove(cache_file)
            print("✓ Кэш очищен")
        except Exception as e:
            print(f"Ошибка очистки кэша: {e}")
    
    def force_reload(self, on_complete=None, on_failed=None, on_progress=None):
        """Принудительная перезагрузка"""
        self.clear_cache()
        self.load_data(on_complete, on_failed, on_progress)

_json_manager = None

def get_json_manager():
    """Получить глобальный экземпляр менеджера"""
    global _json_manager
    if _json_manager is None:
        _json_manager = JsonDataManager()
    return _json_manager