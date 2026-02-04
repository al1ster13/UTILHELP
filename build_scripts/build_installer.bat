@echo off
chcp 65001 >nul
echo ========================================
echo    UTILHELP Installer Builder
echo ========================================
echo.

REM Save current directory
set SCRIPT_DIR=%~dp0
REM Go to project root
cd /d "%SCRIPT_DIR%.."

REM Check if Inno Setup exists
if not exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    echo ERROR: Inno Setup 6 not found!
    echo Download and install Inno Setup from https://jrsoftware.org/isdl.php
    exit /b 1
)

REM Check if executable exists
if not exist "dist\UTILHELP\UTILHELP.exe" (
    echo ERROR: Compiled program not found!
    echo First run 1_build.bat to create exe file
    exit /b 1
)

REM Create output directory
if not exist "installer_output" mkdir installer_output

echo Creating installer...
echo.

REM Compile installer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "%SCRIPT_DIR%utilhelp_installer.iss"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Installer successfully created!
    echo ========================================
    echo.
    echo Installer file: installer_output\UTILHELP_Setup_v1.0.exe
) else (
    echo.
    echo ========================================
    echo   ERROR creating installer!
    echo ========================================
    echo.
    echo Check utilhelp_installer.iss file for errors
    exit /b 1
)