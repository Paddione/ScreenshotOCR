@echo off
echo ScreenshotOCR Windows Client Installer
echo =====================================
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
echo Installing Python dependencies...
echo This may take a few minutes...
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to install dependencies
    echo.
    echo Troubleshooting tips:
    echo 1. Make sure you have Python 3.8 or higher installed
    echo 2. Try running: pip install --upgrade pip
    echo 3. Try running: pip install --user -r requirements.txt
    echo 4. Check your internet connection
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
    echo Try running the alternative installer: install_alternative.bat
)
echo.
pause 