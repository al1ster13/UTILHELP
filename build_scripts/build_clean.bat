@echo off
chcp 65001 >nul
echo ========================================
echo UTILHELP - Clean Build
echo ========================================

REM Save current directory
set SCRIPT_DIR=%~dp0
REM Go to project root
cd /d "%SCRIPT_DIR%.."

REM Clean up completely
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "__pycache__" rmdir /s /q "__pycache__"

REM Clean Python cache
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /r . %%f in (*.pyc) do @if exist "%%f" del "%%f"

echo Cleaned all cache files...

REM Build with clean spec
echo Building UTILHELP...
python -m PyInstaller "%SCRIPT_DIR%utilhelp_structured.spec" --clean --noconfirm

REM Check if build was successful
if not exist "dist\UTILHELP\UTILHELP.exe" (
    echo Build failed!
    exit /b 1
)

echo Build successful! Reorganizing structure...

REM Reorganize structure
python "%SCRIPT_DIR%reorganize_build.py"

if %ERRORLEVEL% NEQ 0 (
    echo Reorganization failed!
    exit /b 1
)

echo ========================================
echo Clean build completed!
echo ========================================

echo File location: dist\UTILHELP\UTILHELP.exe