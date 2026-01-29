@echo off
echo ========================================
echo    UTILHELP Installer Builder
echo ========================================
echo.

REM Сохраняем текущую папку
set SCRIPT_DIR=%~dp0
REM Переходим в корневую папку проекта
cd /d "%SCRIPT_DIR%.."

REM 
if not exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    echo ОШИБКА: Inno Setup 6 не найден!
    echo Скачайте и установите Inno Setup с https://jrsoftware.org/isdl.php
    pause
    exit /b 1
)

REM 
if not exist "dist\UTILHELP\UTILHELP.exe" (
    echo ОШИБКА: Скомпилированная программа не найдена!
    echo Сначала запустите build_final.bat для создания exe файла
    pause
    exit /b 1
)

REM 
if not exist "installer_output" mkdir installer_output

echo Создание установщика...
echo.

REM Компилируем установщик
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "%SCRIPT_DIR%utilhelp_installer.iss"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Установщик успешно создан!
    echo ========================================
    echo.
    echo Файл установщика: installer_output\UTILHELP_Setup_v1.0.exe
    echo.
    
    REM 
    explorer installer_output
    
    echo Нажмите любую клавишу для выхода...
    pause >nul
) else (
    echo.
    echo ========================================
    echo   ОШИБКА при создании установщика!
    echo ========================================
    echo.
    echo Проверьте файл utilhelp_installer.iss на наличие ошибок
    pause
)