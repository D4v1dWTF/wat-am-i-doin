@echo off
title wat am i doin
echo.
echo ========================================
echo    wat am i doin
echo ========================================
echo.
echo Starting wat am i doin...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    echo.
    echo Please install Python from: https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Check if pypresence is installed
python -c "import pypresence" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required library...
    pip install pypresence==4.3.0
    if %errorlevel% neq 0 (
        echo ❌ Failed to install required library!
        echo Please run: pip install pypresence==4.3.0
        echo.
        pause
        exit /b 1
    )
)

echo ✅ Starting wat am i doin...
python DiscordStatusEditor.py

echo.
echo Press any key to exit...
pause >nul 