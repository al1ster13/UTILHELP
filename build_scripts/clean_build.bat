@echo off
chcp 65001 >nul
title Очистка файлов сборки

echo.
echo ============================================================
echo ОЧИСТКА ФАЙЛОВ СБОРКИ
echo ============================================================
echo.

cd /d "%~dp0\.."

echo Удаление папки build...
if exist build (
    rmdir /s /q build
    echo ✓ Папка build удалена
) else (
    echo - Папка build не существует
)

echo.
echo Удаление папки dist...
if exist dist (
    rmdir /s /q dist
    echo ✓ Папка dist удалена
) else (
    echo - Папка dist не существует
)

echo.
echo Удаление папки installer_output...
if exist installer_output (
    rmdir /s /q installer_output
    echo ✓ Папка installer_output удалена
) else (
    echo - Папка installer_output не существует
)

echo.
echo Удаление __pycache__...
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    rmdir /s /q "%%d"
    echo ✓ Удалено: %%d
)

echo.
echo Удаление .pyc файлов...
del /s /q *.pyc 2>nul

echo.
echo ============================================================
echo ✓ ОЧИСТКА ЗАВЕРШЕНА
echo ============================================================
echo.

pause
