@echo off
echo ScreenshotOCR Windows Client - Alternative Installer
echo ===================================================
echo.

echo Checking Python installation...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo.
echo Checking pip installation...
pip --version
if %ERRORLEVEL% NEQ 0 (
    echo Error: pip is not installed or not in PATH
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo.
echo Choose installation method:
echo 1. Standard installation (recommended)
echo 2. User installation (if you don't have admin rights)
echo 3. Force reinstall (if you have existing packages)
echo 4. Install with --no-cache (if you have cache issues)
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Installing with standard method...
    pip install -r requirements.txt
) else if "%choice%"=="2" (
    echo.
    echo Installing with user method...
    pip install --user -r requirements.txt
) else if "%choice%"=="3" (
    echo.
    echo Installing with force reinstall...
    pip install --force-reinstall -r requirements.txt
) else if "%choice%"=="4" (
    echo.
    echo Installing with no cache...
    pip install --no-cache-dir -r requirements.txt
) else (
    echo Invalid choice. Using standard installation...
    pip install -r requirements.txt
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to install dependencies
    echo.
    echo Additional troubleshooting steps:
    echo 1. Try upgrading pip: pip install --upgrade pip
    echo 2. Try installing packages individually:
    echo    pip install requests
    echo    pip install Pillow
    echo    pip install pyautogui
    echo    pip install keyboard
    echo    pip install psutil
    echo    pip install pywin32
    echo    pip install python-dotenv
    echo    pip install schedule
    echo 3. Check if you have Visual Studio Build Tools installed
    echo 4. Try running as administrator
    echo.
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo.
echo Testing installation...
python test_installation.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Installation verified successfully!
    echo.
    echo To start the client, run: python screenshot_client.py
    echo Or double-click: start_client.bat
) else (
    echo.
    echo ⚠️  Installation completed but some packages may have issues.
    echo Check the error messages above for specific problems.
)
echo.
pause 