@echo off
REM ============================================================
REM  Project Tracker AI - Windows build script
REM  Double-click this file, or run it from Command Prompt.
REM
REM  Produces: dist\ProjectTrackerAI.exe   (single standalone file)
REM ============================================================

REM Always run from the folder this .bat file is in, no matter
REM where it was double-clicked from (fixes "doesn't do anything").
cd /d "%~dp0"

echo Working folder: %cd%
echo.

echo [1/5] Checking Python...
where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python was not found on PATH.
    echo Install Python 3.11+ from https://www.python.org/downloads/
    echo IMPORTANT: on the first install screen, check the box
    echo   "Add python.exe to PATH" - then re-run this script.
    goto :fail
)
python --version
echo.

echo [2/5] Creating virtual environment .venv ...
if not exist ".venv\Scripts\activate.bat" (
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: failed to create the virtual environment.
        goto :fail
    )
)
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: failed to activate the virtual environment.
    goto :fail
)
echo.

echo [3/5] Installing build dependencies (this can take a few minutes)...
python -m pip install --upgrade pip
if not exist "requirements-build.txt" (
    echo ERROR: requirements-build.txt not found in %cd%
    echo Make sure you extracted the FULL zip and are running this
    echo script from inside the ProjectTrackerAI-Desktop folder.
    goto :fail
)
pip install -r requirements-build.txt
if errorlevel 1 (
    echo ERROR: dependency install failed. Check your internet connection
    echo and the messages above.
    goto :fail
)
echo.

echo [4/5] Cleaning previous build...
if exist "build\work" rmdir /s /q "build\work"
if exist "dist" rmdir /s /q "dist"
echo.

echo [5/5] Compiling ProjectTrackerAI.exe with PyInstaller...
if not exist "build\pyinstaller.spec" (
    echo ERROR: build\pyinstaller.spec not found in %cd%
    goto :fail
)
pyinstaller build\pyinstaller.spec --distpath dist --workpath build\work --noconfirm
if errorlevel 1 (
    echo ERROR: PyInstaller build failed. Scroll up for the real error.
    goto :fail
)

echo.
echo ============================================================
echo  BUILD COMPLETE:  dist\ProjectTrackerAI.exe
echo  Optional next step: open build\installer.iss with Inno Setup
echo  to produce a proper Setup.exe installer.
echo ============================================================
goto :end

:fail
echo.
echo ============================================================
echo  BUILD FAILED - see the error above.
echo ============================================================

:end
echo.
pause
