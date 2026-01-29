@echo off
REM Build script to create standalone executable using PyInstaller
REM This creates a distributable .exe file that doesn't require Python installation

echo Building standalone executable...
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Build the executable
echo Creating executable...
pyinstaller --onefile --windowed --name="CodeSigningTool" --icon=NONE signertoolgui.py

if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build successful!
echo Executable created in: dist\CodeSigningTool.exe
echo.
pause

