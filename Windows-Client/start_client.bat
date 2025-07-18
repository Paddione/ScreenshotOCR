@echo off
echo Starting ScreenshotOCR Windows Client...
echo.

python screenshot_client.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to start client
    echo Please make sure all dependencies are installed
    echo Run install.bat to install dependencies
    pause
) 