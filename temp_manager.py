import os
import tempfile
import shutil
import atexit
from pathlib import Path


# Импортируем новую систему логирования
try:
    from logger import debug_log
except ImportError:
    # Fallback если logger.py еще не доступен
    def debug_log(message):
        """Временная заглушка для совместимости"""
        print(f"[DEBUG] {message}")


class TempManager:
    """Менеджер временных файлов UTILHELP"""
    
    _instance = None
    _temp_dir = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TempManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Инициализация временной папки"""
        debug_log("TempManager: Starting initialization")
        
        system_temp = tempfile.gettempdir()
        system_temp = os.path.abspath(system_temp)
        debug_log(f"TempManager: System temp dir: {system_temp}")
        
        temp_folder_name = "UTILHELPTEMP"
        self._temp_dir = os.path.join(system_temp, temp_folder_name)
        self._temp_dir = os.path.abspath(os.path.normpath(self._temp_dir))
        debug_log(f"TempManager: Target temp dir: {self._temp_dir}")
        
        try:
            os.makedirs(self._temp_dir, exist_ok=True)
            debug_log(f"TempManager: Created directory: {os.path.exists(self._temp_dir)}")
            
            if os.path.exists(self._temp_dir) and os.access(self._temp_dir, os.W_OK):
                debug_log("TempManager: UTILHELPTEMP initialization successful")
                return
            else:
                debug_log(f"TempManager: UTILHELPTEMP not accessible - exists: {os.path.exists(self._temp_dir)}, writable: {os.access(self._temp_dir, os.W_OK) if os.path.exists(self._temp_dir) else 'N/A'}")
                
        except Exception as e:
            debug_log(f"TempManager: UTILHELPTEMP creation failed: {e}")
        
        try:
            temp_folder_name = "UTILHELP"
            self._temp_dir = os.path.join(system_temp, temp_folder_name)
            self._temp_dir = os.path.abspath(os.path.normpath(self._temp_dir))
            debug_log(f"TempManager: Fallback temp dir: {self._temp_dir}")
            
            os.makedirs(self._temp_dir, exist_ok=True)
            
            if os.path.exists(self._temp_dir) and os.access(self._temp_dir, os.W_OK):
                debug_log("TempManager: UTILHELP fallback successful")
                return
            else:
                debug_log(f"TempManager: UTILHELP fallback not accessible - exists: {os.path.exists(self._temp_dir)}, writable: {os.access(self._temp_dir, os.W_OK) if os.path.exists(self._temp_dir) else 'N/A'}")
                
        except Exception as e2:
            debug_log(f"TempManager: UTILHELP fallback failed: {e2}")
        
        try:
            temp_folder_name = "UH"
            self._temp_dir = os.path.join(system_temp, temp_folder_name)
            self._temp_dir = os.path.abspath(os.path.normpath(self._temp_dir))
            debug_log(f"TempManager: Short fallback temp dir: {self._temp_dir}")
            
            os.makedirs(self._temp_dir, exist_ok=True)
            
            if os.path.exists(self._temp_dir) and os.access(self._temp_dir, os.W_OK):
                debug_log("TempManager: UH short fallback successful")
                return
            else:
                debug_log(f"TempManager: UH short fallback not accessible - exists: {os.path.exists(self._temp_dir)}, writable: {os.access(self._temp_dir, os.W_OK) if os.path.exists(self._temp_dir) else 'N/A'}")
                
        except Exception as e3:
            debug_log(f"TempManager: UH short fallback failed: {e3}")
        
        debug_log("TempManager: Using system temp directly as final fallback")
        self._temp_dir = system_temp
    
    def get_temp_dir(self):
        """Получить путь к временной папке"""
        return self._temp_dir
    
    def get_temp_file_path(self, filename):
        """Получить полный путь к временному файлу"""
        debug_log(f"TempManager: Getting path for filename: {filename}")
        
        if not self._temp_dir:
            debug_log("TempManager: No temp dir, using system temp")
            return os.path.join(tempfile.gettempdir(), filename)
        
        safe_filename = ""
        for c in filename:
            if c.isalnum() or c in "._-()[]{}":
                safe_filename += c
            elif c in " ":
                safe_filename += "_"
        
        debug_log(f"TempManager: Safe filename: {safe_filename}")
        
        if not safe_filename or safe_filename.isspace():
            safe_filename = "download_file.exe"
            debug_log("TempManager: Using default filename")
        elif '.' not in safe_filename:
            safe_filename += ".exe"
            debug_log(f"TempManager: Added .exe extension: {safe_filename}")
        
        if len(safe_filename) > 100:
            name_part, ext_part = os.path.splitext(safe_filename)
            safe_filename = name_part[:90] + ext_part
            debug_log(f"TempManager: Truncated filename: {safe_filename}")
        
        file_path = os.path.join(self._temp_dir, safe_filename)
        debug_log(f"TempManager: Joined path: {file_path}")
        
        file_path = os.path.abspath(os.path.normpath(file_path))
        debug_log(f"TempManager: Final path: {file_path}")
        
        if len(file_path) > 260:
            debug_log(f"TempManager: Path too long ({len(file_path)}), creating short name")
            import time
            short_name = f"utilhelp_{int(time.time())}.exe"
            file_path = os.path.join(self._temp_dir, short_name)
            file_path = os.path.abspath(os.path.normpath(file_path))
            debug_log(f"TempManager: Short path: {file_path}")
        
        return file_path
    
    def cleanup(self):
        """Очистка временной папки и всех временных файлов UTILHELP"""
        try:
            if self._temp_dir and os.path.exists(self._temp_dir):
                debug_log(f"TempManager: Cleaning up temp directory contents: {self._temp_dir}")
                try:
                    for item in os.listdir(self._temp_dir):
                        item_path = os.path.join(self._temp_dir, item)
                        try:
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path, ignore_errors=True)
                        except Exception as e:
                            debug_log(f"TempManager: Failed to remove {item_path}: {e}")
                            pass
                except Exception as e:
                    debug_log(f"TempManager: Failed to list contents of {self._temp_dir}: {e}")
                    pass
            
            system_temp = tempfile.gettempdir()
            
            for folder_name in ["UTILHELPTEMP", "UTILHELP", "UH"]:
                folder_path = os.path.join(system_temp, folder_name)
                if os.path.exists(folder_path):
                    try:
                        debug_log(f"TempManager: Cleaning up folder contents: {folder_path}")
                        for item in os.listdir(folder_path):
                            item_path = os.path.join(folder_path, item)
                            try:
                                if os.path.isfile(item_path):
                                    os.remove(item_path)
                                elif os.path.isdir(item_path):
                                    shutil.rmtree(item_path, ignore_errors=True)
                            except Exception as e:
                                debug_log(f"TempManager: Failed to remove {item_path}: {e}")
                                pass
                    except Exception as e:
                        debug_log(f"TempManager: Failed to list contents of {folder_path}: {e}")
                        pass
            
            try:
                for file in os.listdir(system_temp):
                    file_path = os.path.join(system_temp, file)
                    
                    if (file.startswith("utilhelp") or 
                        file.endswith("_temp.png") or
                        "temp.png" in file):
                        try:
                            if os.path.isfile(file_path):
                                debug_log(f"TempManager: Removing temp file: {file_path}")
                                os.remove(file_path)
                        except:
                            pass
            except:
                pass
                
        except Exception as e:
            debug_log(f"TempManager: Cleanup error: {e}")
            pass  
    
    def create_subfolder(self, subfolder_name):
        """Создать подпапку во временной папке"""
        try:
            safe_name = "".join(c for c in subfolder_name if c.isalnum() or c in "_-")
            if not safe_name:
                safe_name = "subfolder"
            
            subfolder_path = os.path.join(self._temp_dir, safe_name)
            subfolder_path = os.path.abspath(os.path.normpath(subfolder_path))
            
            os.makedirs(subfolder_path, exist_ok=True)
            return subfolder_path
        except Exception as e:
            return self._temp_dir
    
    def ensure_temp_dir_exists(self):
        """Убедиться что временная папка существует и доступна"""
        try:
            if not self._temp_dir:
                debug_log("TempManager: No temp dir set, reinitializing")
                self._initialize()
                return self._temp_dir is not None
            
            system_temp = os.path.abspath(tempfile.gettempdir())
            if self._temp_dir == system_temp:
                debug_log("TempManager: Using system temp, trying to create subfolder")
                
                for folder_name in ["UTILHELPTEMP", "UTILHELP", "UH"]:
                    try:
                        subfolder = os.path.join(system_temp, folder_name)
                        os.makedirs(subfolder, exist_ok=True)
                        
                        if os.path.exists(subfolder) and os.access(subfolder, os.W_OK):
                            self._temp_dir = subfolder
                            debug_log(f"TempManager: Created subfolder: {subfolder}")
                            return True
                    except Exception as e:
                        debug_log(f"TempManager: Failed to create {folder_name}: {e}")
                        continue
                
                debug_log("TempManager: Could not create subfolder, using system temp")
                return True
            
            if not os.path.exists(self._temp_dir):
                debug_log(f"TempManager: Temp dir doesn't exist, creating: {self._temp_dir}")
                os.makedirs(self._temp_dir, exist_ok=True)
            
            if not os.access(self._temp_dir, os.W_OK):
                debug_log(f"TempManager: No write access to: {self._temp_dir}")
                return False
            
            debug_log(f"TempManager: Temp dir OK: {self._temp_dir}")
            return True
            
        except Exception as e:
            debug_log(f"TempManager: ensure_temp_dir_exists failed: {e}")
            return False
    
    def list_temp_files(self):
        """Получить список всех временных файлов"""
        try:
            if os.path.exists(self._temp_dir):
                return [f for f in os.listdir(self._temp_dir) if os.path.isfile(os.path.join(self._temp_dir, f))]
            return []
        except Exception as e:
            return []
    
    def get_temp_size(self):
        """Получить размер временной папки в байтах"""
        try:
            total_size = 0
            if os.path.exists(self._temp_dir):
                for dirpath, dirnames, filenames in os.walk(self._temp_dir):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        if os.path.exists(filepath):
                            total_size += os.path.getsize(filepath)
            return total_size
        except Exception as e:
            return 0
    
    def format_size(self, size_bytes):
        """Форматирование размера в читаемый вид"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def manual_cleanup(self):
        """Ручная очистка всех временных файлов UTILHELP"""
        cleaned_files = []
        
        try:
            system_temp = tempfile.gettempdir()
            
            for folder_name in ["UTILHELPTEMP", "UTILHELP", "UH"]:
                folder_path = os.path.join(system_temp, folder_name)
                if os.path.exists(folder_path):
                    try:
                        for item in os.listdir(folder_path):
                            item_path = os.path.join(folder_path, item)
                            try:
                                if os.path.isfile(item_path):
                                    os.remove(item_path)
                                    cleaned_files.append(f"Файл: {item}")
                                elif os.path.isdir(item_path):
                                    shutil.rmtree(item_path, ignore_errors=True)
                                    cleaned_files.append(f"Папка: {item}")
                            except Exception as e:
                                debug_log(f"TempManager: Failed to remove {item_path}: {e}")
                                pass
                    except Exception as e:
                        debug_log(f"TempManager: Failed to list contents of {folder_path}: {e}")
                        pass
            
            try:
                for file in os.listdir(system_temp):
                    file_path = os.path.join(system_temp, file)
                    
                    if (file.startswith("utilhelp") or 
                        file.endswith("_temp.png") or
                        "temp.png" in file):
                        try:
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                                cleaned_files.append(f"Файл: {file}")
                        except:
                            pass
            except:
                pass
                
        except Exception as e:
            debug_log(f"TempManager: manual_cleanup error: {e}")
            pass
        
        return cleaned_files
    
    def get_debug_info(self):
        """Получить отладочную информацию о путях"""
        info = {
            'temp_dir': self._temp_dir,
            'temp_dir_exists': os.path.exists(self._temp_dir) if self._temp_dir else False,
            'temp_dir_writable': os.access(self._temp_dir, os.W_OK) if self._temp_dir and os.path.exists(self._temp_dir) else False,
            'system_temp': tempfile.gettempdir(),
            'system_temp_exists': os.path.exists(tempfile.gettempdir()),
            'current_files': self.list_temp_files(),
            'temp_size': self.get_temp_size()
        }
        return info


temp_manager = TempManager()


def get_temp_manager():
    """Получить экземпляр менеджера временных файлов"""
    return temp_manager