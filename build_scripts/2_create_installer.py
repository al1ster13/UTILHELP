"""
Скрипт 2: Создание установщика UTILHELP с Inno Setup
"""
import os
import sys
import subprocess
from pathlib import Path

# Цвета для вывода
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Печать заголовка"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_step(text):
    """Печать шага"""
    print(f"{Colors.OKCYAN}▶ {text}{Colors.ENDC}")

def print_success(text):
    """Печать успеха"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    """Печать ошибки"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text):
    """Печать предупреждения"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def check_requirements():
    """Проверка необходимых файлов"""
    print_step("Проверка требований...")
    
    # Проверяем наличие dist
    dist_dir = Path("dist/UTILHELP")
    if not dist_dir.exists():
        print_error(f"Папка dist не найдена: {dist_dir}")
        print("Сначала запустите: python build_scripts/1_build_project.py")
        return False
    print_success(f"Папка dist найдена: {dist_dir}")
    
    # Проверяем наличие EXE
    exe_file = dist_dir / "UTILHELP.exe"
    if not exe_file.exists():
        print_error(f"EXE файл не найден: {exe_file}")
        return False
    print_success(f"EXE файл найден: {exe_file}")
    
    # Проверяем наличие ISS файла
    iss_file = Path("build_scripts/utilhelp_installer.iss")
    if not iss_file.exists():
        print_error(f"ISS файл не найден: {iss_file}")
        return False
    print_success(f"ISS файл найден: {iss_file}")
    
    # Проверяем наличие Inno Setup
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
    ]
    
    inno_compiler = None
    for path in inno_paths:
        if Path(path).exists():
            inno_compiler = path
            break
    
    if not inno_compiler:
        print_error("Inno Setup не найден!")
        print("Установите Inno Setup: https://jrsoftware.org/isdl.php")
        return False
    
    print_success(f"Inno Setup найден: {inno_compiler}")
    return inno_compiler


def create_installer_output_dir():
    """Создание папки для установщика"""
    print_step("Создание папки для установщика...")
    
    output_dir = Path("installer_output")
    output_dir.mkdir(exist_ok=True)
    print_success(f"Папка создана: {output_dir}")
    
    return output_dir


def compile_installer(inno_compiler):
    """Компиляция установщика с Inno Setup"""
    print_step("Компиляция установщика...")
    
    iss_file = Path("build_scripts/utilhelp_installer.iss").absolute()
    
    try:
        # Запускаем Inno Setup Compiler
        result = subprocess.run(
            [inno_compiler, str(iss_file)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Выводим результат
        if result.stdout:
            print(result.stdout)
        
        if result.returncode == 0:
            print_success("Inno Setup завершил работу успешно")
            return True
        else:
            print_error("Inno Setup завершился с ошибкой")
            if result.stderr:
                print("\nВывод ошибки:")
                print(result.stderr)
            return False
            
    except Exception as e:
        print_error(f"Ошибка запуска Inno Setup: {e}")
        return False


def verify_installer():
    """Проверка созданного установщика"""
    print_step("Проверка установщика...")
    
    output_dir = Path("installer_output")
    installer_files = list(output_dir.glob("UTILHELP_Setup_*.exe"))
    
    if not installer_files:
        print_error("Установщик не создан")
        return False
    
    installer_file = installer_files[0]
    installer_size_mb = installer_file.stat().st_size / (1024 * 1024)
    
    print_success(f"Установщик создан: {installer_file.name}")
    print_success(f"Размер установщика: {installer_size_mb:.1f} МБ")
    
    return True


def main():
    """Главная функция"""
    print_header("СОЗДАНИЕ УСТАНОВЩИКА UTILHELP")
    
    # Переходим в корень проекта
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    print(f"Рабочая директория: {project_root}\n")
    
    # Проверка требований
    inno_compiler = check_requirements()
    if not inno_compiler:
        print_error("\nСоздание установщика прервано")
        return 1
    
    # Создание папки для установщика
    create_installer_output_dir()
    
    # Компиляция установщика
    if not compile_installer(inno_compiler):
        print_error("\nСоздание установщика не удалось!")
        return 1
    
    # Проверка результатов
    if not verify_installer():
        print_warning("\nУстановщик создан с предупреждениями")
        return 1
    
    print_header("УСТАНОВЩИК СОЗДАН УСПЕШНО")
    print(f"{Colors.OKGREEN}Результат: installer_output/UTILHELP_Setup_v1.1.exe{Colors.ENDC}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
