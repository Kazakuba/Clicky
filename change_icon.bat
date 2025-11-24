@echo off
echo === Clicky Automation Icon Changer ===
echo This script will help you change the application icon and rebuild the app.
echo.

:: Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python not found! Please ensure Python is installed and in your PATH.
    goto end
)

:: Check if an argument was provided
if "%~1"=="" (
    echo No image file specified.
    echo.
    echo Usage options:
    echo   1. Drag and drop an image file onto this batch file
    echo   2. Run with image path: change_icon.bat path\to\your\icon.png
    echo   3. Continue without arguments to use interactive mode
    echo.
    echo Do you want to continue in interactive mode? (Y/N)
    set /p continue=
    if /i "%continue%" neq "Y" goto end
    
    :: Run the conversion script in interactive mode
    python resources\images\convert_to_ico.py
) else (
    :: Run the conversion script with the provided argument
    python resources\images\convert_to_ico.py "%~1"
)

:end
echo.
echo Press any key to exit...
pause >nul 