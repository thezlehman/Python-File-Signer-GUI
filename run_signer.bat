@echo off
REM Code Signing Tool GUI Launcher
REM This batch file launches the signing tool GUI

echo Starting Code Signing Tool...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Run the GUI application
python signertoolgui.py

REM If there was an error, pause so user can see it
if errorlevel 1 (
    echo.
    echo An error occurred. Check the output above.
    pause
)

