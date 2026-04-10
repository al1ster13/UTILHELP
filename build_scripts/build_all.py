"""
Полная сборка UTILHELP: проект + установщик + портативная версия
"""
import sys
import subprocess
from pathlib import Path

def run_script(script_name):
    """Запуск скрипта сборки"""
    script_path = Path(__file__).parent / script_name
    result = subprocess.run([sys.executable, str(script_path)])
    return result.returncode == 0

def main():
    """Главная функция"""
    # Проверяем аргументы командной строки
    create_portable = "--portable" in sys.argv or "-p" in sys.argv
    
    if create_portable:
        print("\n" + "="*60)
        print("ПОЛНАЯ СБОРКА UTILHELP (с портативной версией)")
        print("="*60 + "\n")
        steps_total = 3
    else:
        print("\n" + "="*60)
        print("ПОЛНАЯ СБОРКА UTILHELP")
        print("="*60 + "\n")
        print("Для создания портативной версии используйте: --portable или -p\n")
        steps_total = 2
    
    # Шаг 1: Сборка проекта
    print(f"Шаг 1/{steps_total}: Сборка проекта...")
    if not run_script("1_build_project.py"):
        print("\n❌ Сборка проекта не удалась!")
        return 1
    
    # Шаг 2: Создание установщика
    print(f"\nШаг 2/{steps_total}: Создание установщика...")
    if not run_script("2_create_installer.py"):
        print("\n❌ Создание установщика не удалось!")
        return 1
    
    # Шаг 3: Создание портативной версии (опционально)
    if create_portable:
        print(f"\nШаг 3/{steps_total}: Создание портативной версии...")
        if not run_script("3_create_portable.py"):
            print("\n❌ Создание портативной версии не удалось!")
            return 1
    
    print("\n" + "="*60)
    print("✓ ПОЛНАЯ СБОРКА ЗАВЕРШЕНА УСПЕШНО")
    print("="*60)
    print("\nРезультаты:")
    print("  • Установщик: installer_output/UTILHELP_Setup_v1.1.exe")
    if create_portable:
        print("  • Портативная версия: portable_output/UTILHELP_Portable_v1.1.zip")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
