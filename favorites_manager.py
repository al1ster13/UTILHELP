import json
import os
from typing import List, Dict, Any


class FavoritesManager:
    """Менеджер для работы с избранными программами и драйверами"""
    
    def __init__(self):
        appdata = os.environ.get('APPDATA')
        if appdata:
            data_dir = os.path.join(appdata, 'UTILHELP', 'data')
        else:
            data_dir = "data"
        
        os.makedirs(data_dir, exist_ok=True)
        self.favorites_file = os.path.join(data_dir, "favorites.json")
        self.favorites = self._load_favorites()
    
    def _load_favorites(self) -> Dict[str, List[str]]:
        """Загрузить избранное из файла"""
        if not os.path.exists(self.favorites_file):
            os.makedirs(os.path.dirname(self.favorites_file), exist_ok=True)
            return {"programs": [], "drivers": []}
        
        try:
            with open(self.favorites_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"programs": [], "drivers": []}
    
    def _save_favorites(self):
        """Сохранить избранное в файл"""
        try:
            os.makedirs(os.path.dirname(self.favorites_file), exist_ok=True)
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения избранного: {e}")
    
    def add_to_favorites(self, item_id: str, item_type: str) -> bool:
        """Добавить элемент в избранное"""
        if item_type not in ["programs", "drivers"]:
            return False
        
        if item_id not in self.favorites[item_type]:
            self.favorites[item_type].append(item_id)
            self._save_favorites()
            return True
        return False
    
    def remove_from_favorites(self, item_id: str, item_type: str) -> bool:
        """Удалить элемент из избранного"""
        if item_type not in ["programs", "drivers"]:
            return False
        
        if item_id in self.favorites[item_type]:
            self.favorites[item_type].remove(item_id)
            self._save_favorites()
            return True
        return False
    
    def is_favorite(self, item_id: str, item_type: str) -> bool:
        """Проверить, находится ли элемент в избранном"""
        if item_type not in ["programs", "drivers"]:
            return False
        return item_id in self.favorites[item_type]
    
    def get_favorites(self, item_type: str) -> List[str]:
        """Получить список избранных элементов"""
        if item_type not in ["programs", "drivers"]:
            return []
        return self.favorites[item_type].copy()
    
    def get_all_favorites(self) -> Dict[str, List[str]]:
        """Получить все избранное"""
        return self.favorites.copy()