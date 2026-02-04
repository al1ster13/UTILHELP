# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['../main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../Icons', 'assets/icons'),           # System icons (including new ones: utilhelplogo24.png)
        ('../ProgramImages', 'assets/programs'), # Program images
        ('../version.txt', '.'),                # Version file in root
        ('../docs/INSTALL_INFO.md', 'docs'),    # Installer information
        ('../docs/COPYRIGHT.md', 'docs'),       # Documents in docs/
        ('../LICENSE', '.'),                    # LICENSE in root folder
    ],
    hiddenimports=[
        'subprocess',
        're',
        'requests',
        'json',
        'datetime',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets', 
        'PyQt6.QtGui',
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
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',      # Exclude unnecessary modules
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
        'cv2',
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
    upx=False,  # Disable UPX - main cause of false positives
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../Icons/utilhelp.ico',
    version='../version_info.txt',  # Add version information
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,  # Disable UPX
    upx_exclude=[],
    name='UTILHELP'
)