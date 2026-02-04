@echo off
chcp 65001 >nul
echo ========================================
echo   2. CREATE INSTALLER
echo ========================================
echo.

call build_installer.bat

echo.
if exist "..\installer_output\UTILHELP_Setup_v1.0.exe" (
    echo ✅ INSTALLER CREATED SUCCESSFULLY!
    echo File: installer_output\UTILHELP_Setup_v1.0.exe
    echo.
    echo ========================================
    echo   ALL DONE!
    echo ========================================
    echo.
    echo CREATED FILES:
    echo ✅ dist\UTILHELP\UTILHELP.exe
    echo ✅ installer_output\UTILHELP_Setup_v1.0.exe
    echo.
    echo 🎉 Ready for distribution!
)

pause