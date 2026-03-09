"""
Скрипт для проверки структуры настроек
"""
from localization import t, get_localization
from settings_manager import settings_manager

def check_settings_structure():
    """Проверка структуры настроек уведомлений"""
    
    localization = get_localization()
    localization.set_language("ru")
    
    print("=" * 60)
    print("ПРОВЕРКА СТРУКТУРЫ НАСТРОЕК УВЕДОМЛЕНИЙ")
    print("=" * 60)
    print()
    
    # Проверка переводов
    print("1. ПРОВЕРКА ПЕРЕВОДОВ:")
    print("-" * 60)
    
    translations = [
        ("notifications.notifications_setting", "Название настройки уведомлений"),
        ("notifications.notifications_hint", "Подсказка для уведомлений"),
        ("notifications.notification_style", "Название стиля уведомлений"),
        ("notifications.style_custom", "Кастомный стиль"),
        ("notifications.style_system", "Системный стиль"),
        ("notifications.notification_sounds", "Название звуков"),
        ("notifications.notification_sounds_hint", "Подсказка для звуков"),
    ]
    
    all_ok = True
    for key, description in translations:
        try:
            value = t(key)
            if key in value:  # Если ключ не переведен, он возвращается как есть
                print(f"  ✗ {description}: ОТСУТСТВУЕТ ({key})")
                all_ok = False
            else:
                print(f"  ✓ {description}: '{value}'")
        except Exception as e:
            print(f"  ✗ {description}: ОШИБКА - {e}")
            all_ok = False
    
    print()
    
    # Проверка настроек
    print("2. ПРОВЕРКА НАСТРОЕК В settings_manager:")
    print("-" * 60)
    
    settings = [
        ("notifications_enabled", True, "Уведомления включены"),
        ("notification_style", "custom", "Стиль уведомлений"),
        ("notification_sounds", True, "Звуки уведомлений"),
    ]
    
    for key, default, description in settings:
        try:
            value = settings_manager.get_setting(key, default)
            print(f"  ✓ {description}: {value}")
        except Exception as e:
            print(f"  ✗ {description}: ОШИБКА - {e}")
            all_ok = False
    
    print()
    
    # Проверка методов в settings_tab_full
    print("3. ПРОВЕРКА МЕТОДОВ В settings_tab_full.py:")
    print("-" * 60)
    
    try:
        from ui.settings.settings_tab_full import SettingsTab
        
        methods = [
            "save_notifications_state",
            "save_notification_sounds",
        ]
        
        for method_name in methods:
            if hasattr(SettingsTab, method_name):
                print(f"  ✓ Метод {method_name} найден")
            else:
                print(f"  ✗ Метод {method_name} НЕ НАЙДЕН")
                all_ok = False
                
    except Exception as e:
        print(f"  ✗ Ошибка импорта SettingsTab: {e}")
        all_ok = False
    
    print()
    print("=" * 60)
    
    if all_ok:
        print("✓ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        print()
        print("Настройки уведомлений должны отображаться в интерфейсе:")
        print("  Настройки → Интерфейс → (после языка)")
        print()
        print("Добавлено 2 настройки:")
        print("  1. Уведомления (completenotif.png)")
        print("  2. Звуки уведомлений (speed.png)")
    else:
        print("✗ ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")
        print("Проверьте файлы и исправьте ошибки.")
    
    print("=" * 60)

if __name__ == "__main__":
    check_settings_structure()
