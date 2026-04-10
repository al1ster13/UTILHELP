"""
Система локализации UTILHELP
Поддержка мультиязычности интерфейса
"""
import json
import os
from typing import Dict, Any


class Localization:
    """Менеджер локализации"""
    
    def __init__(self):
        self.current_language = "ru"
        self.translations = {}
        self.available_languages = {
            "ru": "Русский",
            "en": "English"
        }
        self.load_translations()
    
    def load_translations(self):
        """Загрузить все переводы"""
        import sys
        
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        locales_dir = os.path.join(base_path, "locales")
        
        if not os.path.exists(locales_dir):
            print(f"⚠️ Папка locales не найдена: {locales_dir}")
            if getattr(sys, 'frozen', False):
                locales_dir = os.path.join(sys._MEIPASS, "locales")
            else:
                locales_dir = "locales"
            if not os.path.exists(locales_dir):
                os.makedirs(locales_dir, exist_ok=True)
        
        for lang_code in self.available_languages.keys():
            locale_file = os.path.join(locales_dir, f"{lang_code}.json")
            
            if os.path.exists(locale_file):
                try:
                    with open(locale_file, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                    print(f"✓ Локализация загружена: {lang_code} ({locale_file})")
                except Exception as e:
                    print(f"✗ Ошибка загрузки локализации {lang_code}: {e}")
                    self.translations[lang_code] = {}
            else:
                print(f"⚠️ Файл локализации не найден: {locale_file}")
                self.translations[lang_code] = {}
    
    def set_language(self, lang_code: str):
        """Установить текущий язык"""
        if lang_code in self.available_languages:
            self.current_language = lang_code
            return True
        return False
    
    def get_language(self) -> str:
        """Получить текущий язык"""
        return self.current_language
    
    def get_available_languages(self) -> Dict[str, str]:
        """Получить список доступных языков"""
        return self.available_languages.copy()
    
    def t(self, key: str, **kwargs) -> str:
        """
        Получить перевод по ключу
        
        Args:
            key: Ключ перевода (например, "main_window.title")
            **kwargs: Параметры для форматирования строки
        
        Returns:
            Переведенная строка или ключ если перевод не найден
        """
        keys = key.split('.')
        translation = self.translations.get(self.current_language, {})
        
        for k in keys:
            if isinstance(translation, dict):
                translation = translation.get(k)
            else:
                return key
        
        if translation is None:
            return key
        
        if kwargs:
            try:
                return translation.format(**kwargs)
            except:
                return translation
        
        return translation
    
    def get_language_name(self, lang_code: str = None) -> str:
        """Получить название языка"""
        if lang_code is None:
            lang_code = self.current_language
        return self.available_languages.get(lang_code, lang_code)


_localization = None


def get_localization() -> Localization:
    """Получить глобальный экземпляр локализации"""
    global _localization
    if _localization is None:
        _localization = Localization()
    return _localization


def t(key: str, **kwargs) -> str:
    """Быстрый доступ к переводу"""
    return get_localization().t(key, **kwargs)


def translate_category(category: str) -> str:
    """
    Перевести название категории из JSON
    
    Args:
        category: Название категории на русском (из JSON)
    
    Returns:
        Переведенное название категории
    """
    category_mapping = {
        "Браузеры": "categories.browsers",
        "Архиваторы": "categories.archivers",
        "Графика": "categories.graphics",
        "Дизайн": "categories.design",
        "Игровые платформы": "categories.gaming_platforms",
        "Медиа": "categories.media",
        "Офис": "categories.office",
        "Разработка": "categories.development",
        "Системные утилиты": "categories.system_utils",
        "Системный анализатор": "categories.system_analyzer",
        "Загрузки": "categories.downloads",
        "GPU драйверы": "categories.gpu_drivers",
        "CPU драйверы": "categories.cpu_drivers",
        "Аудио драйверы": "categories.audio_drivers",
        "Сетевые драйверы": "categories.network_drivers",
        "Чипсет": "categories.chipset",
        "Системные библиотеки": "categories.system_libraries"
    }
    
    if category in category_mapping:
        return t(category_mapping[category])
    
    return category


def get_localized_description(item_data: dict) -> str:
    """
    Получить описание на текущем языке
    
    Args:
        item_data: Данные программы/драйвера из JSON
    
    Returns:
        Описание на текущем языке
    """
    current_lang = get_localization().get_language()
    
    if current_lang == "en" and "description_en" in item_data:
        return item_data["description_en"]
    
    return item_data.get("description", "")


def get_localized_news_title(news_item: dict) -> str:
    """
    Получить заголовок новости на текущем языке
    
    Args:
        news_item: Данные новости из JSON
    
    Returns:
        Заголовок на текущем языке
    """
    current_lang = get_localization().get_language()
    
    if current_lang == "en" and "title_en" in news_item:
        return news_item["title_en"]
    
    return news_item.get("title", "")


def get_localized_news_content(news_item: dict) -> str:
    """
    Получить содержимое новости на текущем языке
    
    Args:
        news_item: Данные новости из JSON
    
    Returns:
        Содержимое на текущем языке
    """
    current_lang = get_localization().get_language()
    
    if current_lang == "en" and "content_en" in news_item:
        return news_item["content_en"]
    
    # Иначе возвращаем русское содержимое (по умолчанию)
    return news_item.get("content", "")
