@echo off
echo Running ScreenshotOCR Windows Client Tests...
echo.

python test_client.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo All tests passed! The client is ready to use.
) else (
    echo.
    echo Some tests failed. Please check the output above.
)

pause 