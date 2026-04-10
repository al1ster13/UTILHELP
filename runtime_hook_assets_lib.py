"""
Runtime hook для PyInstaller
Добавляет assets/lib в PATH для поиска DLL
"""
import sys
import os

if getattr(sys, 'frozen', False):
    app_dir = os.path.dirname(sys.executable)
else:
    app_dir = os.path.dirname(os.path.abspath(__file__))

assets_lib = os.path.join(app_dir, 'assets', 'lib')
if os.path.exists(assets_lib):
    os.environ['PATH'] = assets_lib + os.pathsep + os.environ.get('PATH', '')
    
    if assets_lib not in sys.path:
        sys.path.insert(0, assets_lib)
    
    print(f"✅ Added to PATH: {assets_lib}")
