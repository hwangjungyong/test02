@echo off
REM ========================================
REM Install Auto-Start Script
REM Windows 시작 프로그램에 자동 실행 등록
REM ========================================

REM Set code page to Korean (CP949)
chcp 949 >nul 2>&1
if errorlevel 1 chcp 949

echo ========================================
echo Auto-Start Installation Script
echo ========================================
echo.
echo This script will:
echo   1. Create a shortcut in Windows Startup folder
echo   2. Configure servers to start automatically on boot
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul
echo.

REM Get current directory
set "CURRENT_DIR=%~dp0"
set "SCRIPT_PATH=%CURRENT_DIR%auto-start-servers.bat"

REM Get Windows Startup folder path
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

echo [1/3] Creating shortcut in Startup folder...
echo Startup folder: %STARTUP_FOLDER%
echo Script path: %SCRIPT_PATH%
echo.

REM Create shortcut using PowerShell
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTUP_FOLDER%\Auto-Start-Servers.lnk'); $Shortcut.TargetPath = '%SCRIPT_PATH%'; $Shortcut.WorkingDirectory = '%CURRENT_DIR%'; $Shortcut.Description = 'Auto-start development servers'; $Shortcut.Save()"

if errorlevel 1 (
    echo Error: Failed to create shortcut
    echo Please run this script as Administrator
    pause
    exit /b 1
)

echo [2/3] Shortcut created successfully!
echo.

REM Create a batch file that runs in background
echo [3/3] Creating background runner script...
(
echo @echo off
echo REM Auto-start servers in background
echo start /min "" "%SCRIPT_PATH%"
) > "%STARTUP_FOLDER%\Auto-Start-Servers-Runner.bat"

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo The servers will now start automatically when Windows boots.
echo.
echo To disable auto-start:
echo   1. Delete: %STARTUP_FOLDER%\Auto-Start-Servers.lnk
echo   2. Delete: %STARTUP_FOLDER%\Auto-Start-Servers-Runner.bat
echo.
echo To start servers manually:
echo   Run: auto-start-servers.bat
echo.
pause

