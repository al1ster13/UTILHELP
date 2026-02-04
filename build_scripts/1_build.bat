@echo off
chcp 65001 >nul

echo ========================================
echo   1. BUILD PROGRAM
echo ========================================
echo.

REM Go to project root to call build_clean.bat
cd /d "%~dp0.."
call "build_scripts_git\build_clean.bat"

REM Check return code from build_clean.bat
if %ERRORLEVEL% NEQ 0 (
    echo ❌ BUILD ERROR!
    echo Return code: %ERRORLEVEL%
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Checking build result...

REM Wait a bit for all operations to complete
timeout /t 2 /nobreak >nul

if exist "dist\UTILHELP\UTILHELP.exe" (
    echo ✅ BUILD COMPLETED!
    echo File: dist\UTILHELP\UTILHELP.exe
    for %%A in ("dist\UTILHELP\UTILHELP.exe") do (
        echo Size: %%~zA bytes
    )
    echo.
    echo Next step: 2_installer.bat
) else (
    echo ❌ BUILD ERROR!
    echo File not created: dist\UTILHELP\UTILHELP.exe
    echo.
    echo Checking what was created:
    if exist "dist" (
        echo Contents of dist:
        dir /b "dist"
        if exist "dist\UTILHELP" (
            echo.
            echo Contents of dist\UTILHELP:
            dir /b "dist\UTILHELP"
        )
    ) else (
        echo dist folder not created!
    )
    echo.
    echo Check build errors above
)

pause