"""
Скрипт для компиляции Qt ресурсов в Python модуль
"""
import subprocess
import sys
import os


def compile_resources():
    """Компиляция .qrc файла в .py модуль"""
    qrc_file = "resources.qrc"
    output_file = "resources_rc.py"
    
    if not os.path.exists(qrc_file):
        print(f"❌ Файл {qrc_file} не найден!")
        return False
    
    print(f"🔨 Компиляция {qrc_file} → {output_file}...")
    
    try:
        commands = [
            # PySide6-rcc с генерацией для PyQt6
            ["pyside6-rcc", qrc_file, "-g", "python", "-o", output_file],
            # Fallback на старые версии
            ["pyside2-rcc", qrc_file, "-o", output_file],
            ["pyrcc5", qrc_file, "-o", output_file]
        ]
        
        success = False
        compiler_used = None
        for cmd in commands:
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                compiler_used = cmd[0]
                print(f"✅ Успешно скомпилировано с помощью {compiler_used}")
                print(f"📦 Создан файл: {output_file}")
                success = True
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        if not success:
            print("❌ Не удалось найти компилятор ресурсов!")
            print("\n📝 Установите PySide6:")
            print("   pip install PySide6")
            return False
        
        if compiler_used == "pyside6-rcc" and os.path.exists(output_file):
            print("🔄 Адаптация кода для PyQt6...")
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            content = content.replace('from PySide6', 'from PyQt6')
            content = content.replace('PySide6.', 'PyQt6.')
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Код адаптирован для PyQt6")
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"📊 Размер файла: {file_size:,} байт")
            return True
        else:
            print(f"❌ Файл {output_file} не был создан!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка компиляции: {e}")
        return False


def main():
    """Главная функция"""
    print("=" * 60)
    print("Qt Resource Compiler для UTILHELP")
    print("=" * 60)
    print()
    
    if compile_resources():
        print()
        print("✅ Компиляция завершена успешно!")
        print()
        print("📝 Следующие шаги:")
        print("   1. Импортируйте ресурсы в main.py:")
        print("      import resources_rc")
        print("   2. Используйте ресурсы с префиксом ':/icons/'")
        print("      QPixmap(':/icons/Icons/logo64x64.png')")
        print()
        return 0
    else:
        print()
        print("❌ Компиляция не удалась!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
