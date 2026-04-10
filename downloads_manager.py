import os
import sys
import json
import shutil
from datetime import datetime


class DownloadsManager:
    """Управление загрузками"""
    def __init__(self):
        self.downloads_dir = self.get_downloads_dir()
        self.metadata_file = os.path.join(self.downloads_dir, "downloads.json")
        self.ensure_downloads_dir()
    
    def get_downloads_dir(self):
        """Получить путь к папке загрузок"""
        try:
            from main import get_downloads_dir
            return get_downloads_dir()
        except:
            appdata = os.environ.get('APPDATA')
            if appdata:
                return os.path.join(appdata, 'UTILHELP', 'UTILHELPFILES')
            else:
                if getattr(sys, 'frozen', False):
                    base_dir = os.path.dirname(sys.executable)
                else:
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                return os.path.join(base_dir, "UTILHELPFILES")
    
    def ensure_downloads_dir(self):
        """Создать папку загрузок если не существует"""
        try:
            os.makedirs(self.downloads_dir, exist_ok=True)
        except Exception as e:
            print(f"Ошибка создания папки загрузок: {e}")
    
    def add_download(self, filename, original_name, file_type="program", icon_path=None):
        metadata = self.load_metadata()
        
        download_info = {
            "filename": filename,
            "original_name": original_name,
            "file_type": file_type,
            "download_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file_size": self.get_file_size(filename),
            "icon_path": icon_path
        }
        
        metadata.append(download_info)
        self.save_metadata(metadata)
    
    def load_metadata(self):
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_metadata(self, metadata):
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения метаданных: {e}")
    
    def get_downloads(self):
        """Получить список всех загрузок"""
        metadata = self.load_metadata()
        
        valid_downloads = []
        for item in metadata:
            filepath = os.path.join(self.downloads_dir, item["filename"])
            if os.path.exists(filepath):
                item["filepath"] = filepath
                valid_downloads.append(item)
        
        if len(valid_downloads) != len(metadata):
            self.save_metadata(valid_downloads)
        
        return valid_downloads
    
    def delete_download(self, filename):
        filepath = os.path.join(self.downloads_dir, filename)
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
            
            metadata = self.load_metadata()
            metadata = [item for item in metadata if item["filename"] != filename]
            self.save_metadata(metadata)
            
            return True
        except Exception as e:
            print(f"Ошибка удаления файла: {e}")
            return False
    
    def delete_all_downloads(self):
        """Удалить все загрузки"""
        try:
            # Удаляем все файлы
            metadata = self.load_metadata()
            for item in metadata:
                filepath = os.path.join(self.downloads_dir, item["filename"])
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except Exception as e:
                        print(f"Ошибка удаления файла {filepath}: {e}")
            
            # Очищаем метаданные
            self.save_metadata([])
            
            return True
        except Exception as e:
            print(f"Ошибка удаления всех файлов: {e}")
            return False
    
    def get_file_size(self, filename):
        """Получить размер файла в читаемом формате"""
        filepath = os.path.join(self.downloads_dir, filename)
        
        try:
            size_bytes = os.path.getsize(filepath)
            
            for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024.0
            
            return f"{size_bytes:.1f} ТБ"
        except:
            return "Неизвестно"
    
    def get_total_size(self):
        """Получить общий размер всех загрузок"""
        total = 0
        for item in self.get_downloads():
            try:
                filepath = item["filepath"]
                total += os.path.getsize(filepath)
            except:
                pass
        
        size_bytes = total
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.1f} ТБ"


_downloads_manager = None

def get_downloads_manager():
    """Получить глобальный экземпляр менеджера загрузок"""
    global _downloads_manager
    if _downloads_manager is None:
        _downloads_manager = DownloadsManager()
    return _downloads_manager
