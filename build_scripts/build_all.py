"""
Полная сборка UTILHELP: проект + установщик
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
    print("\n" + "="*60)
    print("ПОЛНАЯ СБОРКА UTILHELP")
    print("="*60 + "\n")
    
    # Шаг 1: Сборка проекта
    print("Шаг 1/2: Сборка проекта...")
    if not run_script("1_build_project.py"):
        print("\n❌ Сборка проекта не удалась!")
        return 1
    
    # Шаг 2: Создание установщика
    print("\nШаг 2/2: Создание установщика...")
    if not run_script("2_create_installer.py"):
        print("\n❌ Создание установщика не удалось!")
        return 1
    
    print("\n" + "="*60)
    print("✓ ПОЛНАЯ СБОРКА ЗАВЕРШЕНА УСПЕШНО")
    print("="*60)
    print("\nРезультат: installer_output/UTILHELP_Setup_v1.1.exe\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
