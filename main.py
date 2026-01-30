import sys
import ctypes
import os
import tempfile
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, QSharedMemory
from splash_screen import SplashScreen
from main_window import MainWindow
from temp_manager import get_temp_manager
from json_data_manager import get_json_manager


def is_portable_mode():
    """Определение портативного режима по наличию маркера"""
    try:
        # Получаем путь к папке с программой
        if getattr(sys, 'frozen', False):
            # Если программа скомпилирована
            app_dir = os.path.dirname(sys.executable)
        else:
            # Если запускается из исходников
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Проверяем наличие маркера портативной версии
        portable_marker = os.path.join(app_dir, "PORTABLE_MODE.txt")
        return os.path.exists(portable_marker)
    except:
        return False


def get_app_data_dir():
    """Получение папки для данных приложения"""
    if is_portable_mode():
        # В портативном режиме используем папку программы
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))
    else:
        # В обычном режиме используем текущую папку
        return os.getcwd()


def setup_portable_environment():
    """Настройка окружения для портативного режима"""
    if is_portable_mode():
        app_dir = get_app_data_dir()
        
        # Создаем необходимые папки
        data_dir = os.path.join(app_dir, "data")
        uhdownload_dir = os.path.join(app_dir, "UHDOWNLOAD")
        
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(uhdownload_dir, exist_ok=True)
        
        # Меняем рабочую директорию на папку программы
        os.chdir(app_dir)
        
        print(f"✓ Portable mode enabled - working directory: {app_dir}")
        return True
    
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
            from temp_manager import debug_log
            debug_log("Program exit - temp files preserved")
        except:
            pass
    except Exception as e:
        pass

shared_memory = None 

if __name__ == "__main__":
    print("Запуск программы...")
    
    # Настройка портативного режима
    setup_portable_environment()
    
    print("Создание QApplication...")
    app = QApplication(sys.argv)
    
    # Устанавливаем иконку приложения для панели задач
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
            print(f"✗ Ошибка загрузки данных: {error}")
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