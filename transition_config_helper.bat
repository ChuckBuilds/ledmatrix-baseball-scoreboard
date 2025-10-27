@echo off
echo LEDMatrix Transition Configuration Helper
echo =========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "src\display_transitions.py" (
    echo Error: display_transitions.py not found
    echo Please run this script from the LEDMatrix root directory
    pause
    exit /b 1
)

echo Getting transition recommendations for your display...
echo.

REM Run the config helper script
python transition_config_helper.py %1 %2

echo.
echo Press any key to exit.
pause >nul
