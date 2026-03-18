@echo off
title FB Profile Manager
color 0B
cls

echo.
echo  ============================================================
echo   FB PROFILE MANAGER - Starting...
echo  ============================================================
echo.

:: -- Find Python ----------------------------------------------
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python not found!
    echo  Please install Python from https://python.org
    echo  Make sure to check "Add Python to PATH" during install!
    pause
    exit /b
)

:: -- Go to the folder where this .bat file lives --------------
cd /d "%~dp0"

:: -- Remove playwright-stealth if installed (conflicts) -------
pip show playwright-stealth >nul 2>&1
if %errorlevel% equ 0 (
    echo  [!] Removing conflicting package: playwright-stealth...
    pip uninstall playwright-stealth -y >nul 2>&1
)

:: -- Check greenlet (prebuilt binary only, >=3.1.1) -----------
python -c "import greenlet; from packaging.version import Version; assert Version(greenlet.__version__) >= Version('3.1.1')" >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Installing greenlet...
    pip install "greenlet>=3.1.1" --only-binary=:all: >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [ERROR] Failed to install greenlet.
        pause
        exit /b
    )
)

:: -- Check Playwright -----------------------------------------
python -c "import playwright" >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Installing Playwright...
    pip install playwright >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [ERROR] Failed to install Playwright.
        pause
        exit /b
    )
    echo  [!] Installing Chromium browser...
    playwright install chromium
)

:: -- Check PyQt6 ----------------------------------------------
python -c "import PyQt6" >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Installing PyQt6...
    pip install PyQt6 >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [ERROR] Failed to install PyQt6.
        pause
        exit /b
    )
)

:: -- Launch GUI -----------------------------------------------
echo  [+] Launching FB Profile Manager...
echo.
python gui.py

if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Something went wrong. See message above.
    pause
)
