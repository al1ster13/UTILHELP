@echo off
chcp 65001 >nul
title Полная сборка UTILHELP

echo.
echo ============================================================
echo ПОЛНАЯ СБОРКА UTILHELP
echo ============================================================
echo.
echo Выберите режим сборки:
echo   1 - Установщик (по умолчанию)
echo   2 - Установщик + Портативная версия
echo.

set /p choice="Ваш выбор (1 или 2): "

if "%choice%"=="" set choice=1
if "%choice%"=="1" (
    set CREATE_PORTABLE=0
    set STEPS=2
) else if "%choice%"=="2" (
    set CREATE_PORTABLE=1
    set STEPS=3
) else (
    echo Неверный выбор. Используется режим по умолчанию.
    set CREATE_PORTABLE=0
    set STEPS=2
)

echo.
cd /d "%~dp0\.."

echo Шаг 1/%STEPS%: Сборка проекта...
echo.
python build_scripts\1_build_project.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================================
    echo ✗ СБОРКА ПРОЕКТА НЕ УДАЛАСЬ
    echo ============================================================
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo ✓ Проект собран успешно
echo ============================================================
echo.
echo Шаг 2/%STEPS%: Создание установщика...
echo.

python build_scripts\2_create_installer.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================================
    echo ✗ СОЗДАНИЕ УСТАНОВЩИКА НЕ УДАЛОСЬ
    echo ============================================================
    echo.
    pause
    exit /b 1
)

if %CREATE_PORTABLE%==1 (
    echo.
    echo ============================================================
    echo ✓ Установщик создан успешно
    echo ============================================================
    echo.
    echo Шаг 3/%STEPS%: Создание портативной версии...
    echo.
    
    python build_scripts\3_create_portable.py
    
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ============================================================
        echo ✗ СОЗДАНИЕ ПОРТАТИВНОЙ ВЕРСИИ НЕ УДАЛОСЬ
        echo ============================================================
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ============================================================
echo ✓ ПОЛНАЯ СБОРКА ЗАВЕРШЕНА УСПЕШНО
echo ============================================================
echo.
echo Результаты:
echo   • Установщик: installer_output\UTILHELP_Setup_v1.1.exe

if %CREATE_PORTABLE%==1 (
    echo   • Портативная версия: portable_output\UTILHELP_Portable_v1.1.zip
)

echo.
pause
