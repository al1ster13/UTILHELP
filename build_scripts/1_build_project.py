"""
Скрипт 1: Сборка проекта UTILHELP с PyInstaller
"""
import os
import sys
import shutil
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
    """Проверка необходимых файлов и зависимостей"""
    print_step("Проверка требований...")
    
    # Проверяем наличие PyInstaller
    try:
        import PyInstaller
        print_success(f"PyInstaller установлен (версия {PyInstaller.__version__})")
    except ImportError:
        print_error("PyInstaller не установлен!")
        print("Установите: pip install pyinstaller")
        return False
    
    # Проверяем наличие spec файла
    spec_file = Path("build_scripts/utilhelp_structured.spec")
    if not spec_file.exists():
        print_error(f"Spec файл не найден: {spec_file}")
        return False
    print_success(f"Spec файл найден: {spec_file}")
    
    # Проверяем наличие resources_rc.py
    resources_file = Path("resources_rc.py")
    if not resources_file.exists():
        print_warning("resources_rc.py не найден!")
        print("Запустите: python compile_resources.py")
        return False
    print_success(f"Qt ресурсы найдены: {resources_file}")
    
    # Проверяем размер resources_rc.py
    size_mb = resources_file.stat().st_size / (1024 * 1024)
    if size_mb < 1.5:
        print_warning(f"resources_rc.py слишком маленький ({size_mb:.1f} МБ)")
        print("Возможно, не все ресурсы включены. Перекомпилируйте: python compile_resources.py")
    else:
        print_success(f"Размер ресурсов: {size_mb:.1f} МБ")
    
    return True


def clean_build_dirs():
    """Очистка старых файлов сборки"""
    print_step("Очистка старых файлов сборки...")
    
    dirs_to_clean = ["build", "dist"]
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print_success(f"Удалена папка: {dir_name}")
            except Exception as e:
                print_warning(f"Не удалось удалить {dir_name}: {e}")
        else:
            print(f"  Папка {dir_name} не существует")
    
    print()


def build_with_pyinstaller():
    """Сборка проекта с PyInstaller"""
    print_step("Запуск PyInstaller...")
    
    spec_file = "build_scripts/utilhelp_structured.spec"
    
    try:
        # Запускаем PyInstaller
        result = subprocess.run(
            ["pyinstaller", spec_file, "--clean", "--noconfirm"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            print_success("PyInstaller завершил работу успешно")
            return True
        else:
            print_error("PyInstaller завершился с ошибкой")
            print("\nВывод ошибки:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print_error(f"Ошибка запуска PyInstaller: {e}")
        return False


def verify_build():
    """Проверка результатов сборки"""
    print_step("Проверка результатов сборки...")
    
    dist_dir = Path("dist/UTILHELP")
    if not dist_dir.exists():
        print_error(f"Папка dist не создана: {dist_dir}")
        return False
    
    exe_file = dist_dir / "UTILHELP.exe"
    if not exe_file.exists():
        print_error(f"EXE файл не создан: {exe_file}")
        return False
    
    exe_size_mb = exe_file.stat().st_size / (1024 * 1024)
    print_success(f"EXE файл создан: {exe_file} ({exe_size_mb:.1f} МБ)")
    
    # Проверяем наличие DLL
    dll_files = list(dist_dir.glob("*.dll"))
    print_success(f"Найдено DLL файлов: {len(dll_files)}")
    
    # Проверяем что НЕТ папок Icons и ProgramImages
    icons_dir = dist_dir / "Icons"
    programs_dir = dist_dir / "ProgramImages"
    
    if icons_dir.exists():
        print_warning("Папка Icons найдена в dist (должна быть в QRC)")
    else:
        print_success("Папка Icons отсутствует (иконки в QRC) ✓")
    
    if programs_dir.exists():
        print_warning("Папка ProgramImages найдена в dist (должна быть в QRC)")
    else:
        print_success("Папка ProgramImages отсутствует (иконки в QRC) ✓")
    
    # Проверяем наличие locales
    locales_dir = dist_dir / "locales"
    if locales_dir.exists():
        locale_files = list(locales_dir.glob("*.json"))
        print_success(f"Найдено файлов локализации: {len(locale_files)}")
    else:
        print_warning("Папка locales не найдена")
    
    return True


def main():
    """Главная функция"""
    print_header("СБОРКА ПРОЕКТА UTILHELP")
    
    # Переходим в корень проекта
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    print(f"Рабочая директория: {project_root}\n")
    
    # Проверка требований
    if not check_requirements():
        print_error("\nСборка прервана из-за отсутствия требований")
        return 1
    
    # Очистка старых файлов
    clean_build_dirs()
    
    # Сборка
    if not build_with_pyinstaller():
        print_error("\nСборка не удалась!")
        return 1
    
    # Проверка результатов
    if not verify_build():
        print_warning("\nСборка завершена с предупреждениями")
        return 1
    
    print_header("СБОРКА ЗАВЕРШЕНА УСПЕШНО")
    print(f"{Colors.OKGREEN}Результат: dist/UTILHELP/{Colors.ENDC}")
    print(f"\n{Colors.OKCYAN}Следующий шаг: python build_scripts/2_create_installer.py{Colors.ENDC}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
