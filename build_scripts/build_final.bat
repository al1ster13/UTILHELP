@echo off
chcp 65001 >nul
echo ========================================
echo UTILHELP - Final Build with Structure
echo ========================================

REM Save current directory
set SCRIPT_DIR=%~dp0
REM Go to project root
cd /d "%SCRIPT_DIR%.."

REM Clean up
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM Build executable
echo Building executable with structured spec...
python -m PyInstaller "%SCRIPT_DIR%utilhelp_structured.spec" --clean

REM Check if build was successful
if not exist "dist\UTILHELP\UTILHELP.exe" (
    echo Build failed!
    pause
    exit /b 1
)

echo Build successful! Reorganizing structure...

REM Reorganize structure
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
echo   └── _internal\            (PyQt6 libraries and system files)

echo.
echo Test the executable: dist\UTILHELP\UTILHELP.exe
echo Ready for your custom installer!

pause