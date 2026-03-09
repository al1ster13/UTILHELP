# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
import os

block_cipher = None

# Получаем абсолютный путь к корню проекта
spec_root = os.path.abspath(SPECPATH)
project_root = os.path.dirname(spec_root)

# Собираем все подмодули
core_modules = collect_submodules('core')
ui_modules = collect_submodules('ui')

a = Analysis(
    [os.path.join(project_root, 'main.py')],
    pathex=[project_root],
    binaries=[],
    datas=[
        # Иконки программ и системные иконки теперь в QRC (resources_rc.py)
        # Не включаем Icons и ProgramImages - они встроены в DLL
        (os.path.join(project_root, 'version.txt'), '.'),
        (os.path.join(project_root, 'LICENSE'), '.'),
    ],
    hiddenimports=[
        # Стандартные библиотеки
        'subprocess',
        're',
        'requests',
        'json',
        'datetime',
        'os',
        'sys',
        'pathlib',
        'typing',
        'traceback',
        'tempfile',
        'shutil',
        'webbrowser',
        'platform',
        
        # PyQt6
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets', 
        'PyQt6.QtGui',
        'PyQt6.QtNetwork',
        
        # Корневые модули
        'custom_dialogs',
        'download_manager',
        'downloads_manager',
        'downloads_tab',
        'drivers_tab',
        'favorites_manager',
        'gpu_detector',
        'image_helper',
        'json_data_manager',
        'loading_widget',
        'localization',
        'logger',
        'main_window',
        'news_tab',
        'notification_manager',
        'programs_tab',
        'resource_path',
        'scroll_helper',
        'settings_manager',
        'splash_screen',
        'system_scanner',
        'temp_manager',
        'update_checker',
        'resources_rc',  # Qt Resources
        'resource_extractor',  # Извлечение ресурсов
    ] + core_modules + ui_modules,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
        'cv2',
        'test',
        'unittest',
        'pydoc',
        # Исключаем PySide6 (используем только PyQt6)
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
        'PySide6.QtNetwork',
        'PySide6.QtMultimedia',
        'shiboken6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='UTILHELP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'Icons', 'utilhelp.ico'),
    version=os.path.join(project_root, 'version_info.txt'),
)

# Оставляем все DLL в корне для надежности
# (Перемещение в assets/lib вызывает проблемы с загрузкой)

# Создаем Tree для папок locales и docs - они будут в корне dist/UTILHELP
locales_tree = Tree(
    os.path.join(project_root, 'locales'),
    prefix='locales',  # Папка в корне dist/UTILHELP
    excludes=[]
)

docs_tree = Tree(
    os.path.join(project_root, 'docs'),
    prefix='docs',  # Папка в корне dist/UTILHELP
    excludes=[]
)

coll = COLLECT(
    exe,
    a.binaries,  # Все бинарные файлы в корень
    a.zipfiles,
    a.datas,
    locales_tree,  # Папка locales в корень
    docs_tree,     # Папка docs в корень
    strip=False,
    upx=False,
    upx_exclude=[],
    name='UTILHELP'
)
