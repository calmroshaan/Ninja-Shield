@echo off
title FB Profile Manager - Fix Dependencies
color 0C
cls

echo.
echo  ============================================================
echo   FB PROFILE MANAGER - Fix Dependencies
echo  ============================================================
echo.

cd /d "%~dp0"

:: -- Remove playwright-stealth (conflicts) --------------------
pip show playwright-stealth >nul 2>&1
if %errorlevel% equ 0 (
    echo  [1] Removing playwright-stealth (conflicts)...
    pip uninstall playwright-stealth -y
) else (
    echo  [1] playwright-stealth not installed - skipping.
)
echo.

:: -- greenlet -------------------------------------------------
python -c "import greenlet; from packaging.version import Version; assert Version(greenlet.__version__) >= Version('3.1.1')" >nul 2>&1
if %errorlevel% neq 0 (
    echo  [2] Installing greenlet (prebuilt)...
    pip install "greenlet>=3.1.1" --only-binary=:all:
) else (
    echo  [2] greenlet OK - skipping.
)
echo.

:: -- Playwright -----------------------------------------------
python -c "import playwright" >nul 2>&1
if %errorlevel% neq 0 (
    echo  [3] Installing Playwright...
    pip install playwright
) else (
    echo  [3] Playwright OK - skipping.
)
echo.

:: -- Chromium -------------------------------------------------
echo  [4] Ensuring Chromium is installed...
playwright install chromium
echo.

:: -- PyQt6 ----------------------------------------------------
python -c "import PyQt6" >nul 2>&1
if %errorlevel% neq 0 (
    echo  [5] Installing PyQt6...
    pip install PyQt6
) else (
    echo  [5] PyQt6 OK - skipping.
)
echo.

echo  ============================================================
echo   Done! Run START.bat to launch the tool.
echo  ============================================================
echo.
pause
