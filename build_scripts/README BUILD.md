# Build Scripts

Эта папка содержит все файлы для сборки и создания установщика UTILHELP.

## Файлы

### Batch файлы
- **`build_final.bat`** - Основной скрипт сборки программы
- **`build_installer.bat`** - Создание установщика

### Spec файлы PyInstaller
- **`utilhelp_structured.spec`** - Основной spec файл для PyInstaller
- **`UTILHELP.spec`** - Альтернативный spec файл

### Inno Setup
- **`utilhelp_installer.iss`** - Скрипт для создания установщика

### Python скрипты
- **`reorganize_build.py`** - Реорганизация структуры после сборки

## Использование

### 1. Сборка программы
```bash
cd build_scripts
build_final.bat
```

### 2. Создание установщика
```bash
cd build_scripts
build_installer.bat
```

## Требования

- Python 3.8+
- PyInstaller
- Inno Setup 6 (для создания установщика)

## Структура после сборки

```
dist/UTILHELP/
├── UTILHELP.exe          (Основной исполняемый файл)
├── assets/
│   ├── icons/            (Системные иконки)
│   └── programs/         (Картинки программ)
├── data/                 (Файлы данных)
├── docs/                 (Документация)
├── bat/                  (Утилиты очистки)
└── _internal/            (Библиотеки PyQt6)
```