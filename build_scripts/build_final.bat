@echo off
echo ========================================
echo UTILHELP - Final Build with Structure
echo ========================================

REM Сохраняем текущую папку
set SCRIPT_DIR=%~dp0
REM Переходим в корневую папку проекта
cd /d "%SCRIPT_DIR%.."

REM Очистка
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM 
echo Building executable with structured spec...
python -m PyInstaller "%SCRIPT_DIR%utilhelp_structured.spec" --clean

REM 
if not exist "dist\UTILHELP\UTILHELP.exe" (
    echo Build failed!
    pause
    exit /b 1
)

echo Build successful! Reorganizing structure...

REM 
python "%SCRIPT_DIR%reorganize_build.py"

if %ERRORLEVEL% NEQ 0 (
    echo Reorganization failed!
    pause
    exit /b 1
)

echo ========================================
echo Final structure created!
echo ========================================

echo dist\UTILHELP\
echo   ├── UTILHELP.exe          (Main executable)
echo   ├── assets\
echo   │   ├── icons\            (System icons - PNG/ICO files)
echo   │   └── programs\         (Program images - PNG/JPG files)
echo   ├── data\                 (Database files)
echo   ├── docs\                 (Documentation)
echo   ├── bat\                  (Cleanup utilities)
echo   └── _internal\            (PyQt6 libraries and system files)

echo.
echo Test the executable: dist\UTILHELP\UTILHELP.exe
echo Ready for your custom installer!

pause