import sys
import ctypes
import os
import tempfile
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, QSharedMemory

# Импортируем скомпилированные Qt ресурсы
try:
    import resources_rc
    print("✅ Qt resources loaded")
except ImportError:
    print("⚠️ Qt resources not found, using fallback to file system")

# Извлекаем ресурсы в файловую систему (звуки для QSoundEffect)
try:
    from resource_extractor import extract_resources_on_startup
    if extract_resources_on_startup():
        print("✅ Resources extracted to assets/")
    else:
        print("⚠️ Resource extraction skipped or failed")
except Exception as e:
    print(f"⚠️ Resource extraction error: {e}")

from splash_screen import SplashScreen
from main_window import MainWindow
from temp_manager import get_temp_manager
from json_data_manager import get_json_manager
from logger import get_logger, log_info, log_error, log_warning


def is_portable_mode():
    """Определение портативного режима по наличию маркера"""
    try:
        # Получаем путь к папке с программой
        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        portable_marker = os.path.join(app_dir, "PORTABLE_MODE.txt")
        return os.path.exists(portable_marker)
    except:
        return False


def get_app_data_dir():
    """Получение папки для данных приложения"""
    import sys
    
    if is_portable_mode():
        # В портативном режиме используем папку программы
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))
    else:
        # В обычном режиме ВСЕГДА используем AppData
        appdata = os.environ.get('APPDATA')
        if not appdata:
            # Fallback если APPDATA не определен
            import tempfile
            return os.path.join(tempfile.gettempdir(), 'UTILHELP_data')
        
        utilhelp_data = os.path.join(appdata, 'UTILHELP')
        
        try:
            os.makedirs(utilhelp_data, exist_ok=True)
            test_file = os.path.join(utilhelp_data, 'test_write.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"✓ Using AppData directory: {utilhelp_data}")
            return utilhelp_data
        except Exception as e:
            print(f"✗ Error accessing AppData: {e}")
            # Fallback на временную папку
            import tempfile
            temp_data = os.path.join(tempfile.gettempdir(), 'UTILHELP_data')
            try:
                os.makedirs(temp_data, exist_ok=True)
                print(f"✓ Using temporary directory: {temp_data}")
                return temp_data
            except:
                print("✗ Failed to create any data directory")
                if getattr(sys, 'frozen', False):
                    return os.path.dirname(sys.executable)
                else:
                    return os.path.dirname(os.path.abspath(__file__))


def get_downloads_dir():
    """Получение папки для скачанных файлов"""
    app_data_dir = get_app_data_dir()
    return os.path.join(app_data_dir, "UTILHELPFILES")


def setup_portable_environment():
    """Настройка окружения для портативного режима"""
    app_data_dir = get_app_data_dir()
    
    data_dir = os.path.join(app_data_dir, "data")
    downloads_dir = get_downloads_dir()
    
    try:
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(downloads_dir, exist_ok=True)
        
        test_file = os.path.join(data_dir, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        
        print(f"✓ Data directories created:")
        print(f"  - AppData: {app_data_dir}")
        print(f"  - Data: {data_dir}")
        print(f"  - Downloads: {downloads_dir}")
        
        if is_portable_mode():
            # В портативном режиме меняем рабочую директорию
            os.chdir(app_data_dir)
            print(f"✓ Portable mode enabled - working directory: {app_data_dir}")
        
        return True
        
    except Exception as e:
        log_error(f"✗ Error setting up data directories: {e}")
        # В крайнем случае используем временную папку
        import tempfile
        temp_data = os.path.join(tempfile.gettempdir(), 'UTILHELP_data')
        try:
            os.makedirs(temp_data, exist_ok=True)
            os.makedirs(os.path.join(temp_data, "data"), exist_ok=True)
            os.makedirs(os.path.join(temp_data, "UTILHELPFILES"), exist_ok=True)
            print(f"✓ Using temporary data directory: {temp_data}")
            return True
        except:
            print("✗ Failed to create any data directory")
            return False


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    try:
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
            args = None
        else:
            python_dir = os.path.dirname(sys.executable)
            pythonw_path = os.path.join(python_dir, "pythonw.exe")
            
            if os.path.exists(pythonw_path):
                exe_path = pythonw_path
            else:
                exe_path = sys.executable
            args = f'"{os.path.abspath(__file__)}"'
        
        result = ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            exe_path,
            args,
            None, 
            1  
        )
        return result > 32
    except Exception as e:
        return False

def cleanup_and_exit():
    try:
        temp_manager = get_temp_manager()
        try:
            from logger import log_info
            log_info("Program exit - temp files preserved")
        except:
            pass
    except Exception as e:
        pass

shared_memory = None 

if __name__ == "__main__":
    log_info("=== UTILHELP Starting ===")
    log_info("Запуск программы...")
    
    try:
        setup_portable_environment()
        log_info("Портативное окружение настроено")
    except Exception as e:
        log_error(f"Ошибка настройки портативного окружения: {e}", exc_info=True)
    
    try:
        from localization import get_localization
        from settings_manager import settings_manager
        
        localization = get_localization()
        saved_language = settings_manager.get_setting("language", "ru")
        localization.set_language(saved_language)
        log_info(f"Локализация инициализирована: {saved_language}")
    except Exception as e:
        log_error(f"Ошибка инициализации локализации: {e}", exc_info=True)
    
    log_info("Создание QApplication...")
    app = QApplication(sys.argv)
    
    from resource_path import get_icon_path
    from PyQt6.QtGui import QIcon
    
    icon_path = get_icon_path("utilhelp.ico")
    if icon_path:
        app.setWindowIcon(QIcon(icon_path))
    else:
        # Fallback на PNG иконку
        png_icon_path = get_icon_path("logo64x64.png")
        if png_icon_path:
            app.setWindowIcon(QIcon(png_icon_path))
    
    shared_memory = QSharedMemory("UTILHELP_SINGLE_INSTANCE")
    
    if shared_memory.attach():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("UTILHELP")
        msg.setText("Программа уже запущена!")
        msg.setInformativeText("UTILHELP уже открыт. Вы можете запустить только один экземпляр программы.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
            }
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #555555;
                color: #ffffff;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        msg.exec()
        sys.exit(0)
    
    if not shared_memory.create(1):
        print("Не удалось создать shared memory")
        sys.exit(1)
    
    def cleanup_shared_memory():
        global shared_memory
        if shared_memory:
            shared_memory.detach()
        cleanup_and_exit()
    
    app.aboutToQuit.connect(cleanup_shared_memory)
    
    print("Инициализация temp_manager...")
    temp_manager = get_temp_manager()
    
    system_temp = os.path.abspath(tempfile.gettempdir())
    utilhelp_temp = temp_manager.get_temp_dir()
    
    if utilhelp_temp == system_temp:
        for folder_name in ["UTILHELPTEMP", "UTILHELP", "UH"]:
            try:
                subfolder = os.path.join(system_temp, folder_name)
                os.makedirs(subfolder, exist_ok=True)
                
                if os.path.exists(subfolder) and os.access(subfolder, os.W_OK):
                    # Принудительно устанавливаем новую папку в менеджере
                    temp_manager._temp_dir = subfolder
                    break
            except Exception as e:
                continue
    
    print("Создание splash screen...")
    splash = SplashScreen()
    splash.show()
    splash.start_animation()
    
    print("Создание главного окна...")
    try:
        window = MainWindow()
        print("Главное окно создано успешно")
    except Exception as e:
        print(f"Ошибка создания главного окна: {e}")
        traceback.print_exc()
        sys.exit(1)
    
    def load_initial_data():
        print("Запуск загрузки данных...")
        json_manager = get_json_manager()
        
        def on_data_loaded(data):
            print(f"✓ Данные загружены: программы={len(data['programs'])}, драйверы={len(data['drivers'])}, новости={len(data['news'])}")
            try:
                window.on_data_loaded(data)
            except Exception as e:
                print(f"Ошибка обработки данных: {e}")
                traceback.print_exc()
        
        def on_data_failed(error):
            log_error(f"✗ Ошибка загрузки данных: {error}")
            try:
                window.on_data_failed(error)
            except Exception as e:
                print(f"Ошибка обработки ошибки: {e}")
                traceback.print_exc()
        
        def on_progress(message, percent):
            print(f"Загрузка: {message} ({percent}%)")
        
        try:
            json_manager.load_data(
                on_complete=on_data_loaded,
                on_failed=on_data_failed,
                on_progress=on_progress
            )
        except Exception as e:
            print(f"Ошибка запуска загрузки данных: {e}")
            traceback.print_exc()
    
    QTimer.singleShot(500, load_initial_data)
    
    splash.progress_animation.finished.connect(window.show)
    
    print("Запуск основного цикла приложения...")
    exit_code = app.exec()
    
    sys.exit(exit_code)