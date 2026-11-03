@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "ROOT=%CD%"
title Institute Ledger - Universal Installer Builder (Fixed)
color 0A

echo =============================================================
echo       INSTITUTE LEDGER - UNIVERSAL WINDOWS INSTALLER
echo =============================================================
echo Fixed asset paths; PDF viewing uses the Windows default PDF reader to avoid native build dependencies.
echo It builds separate 32-bit and 64-bit EXEs, then combines them into one installer.
echo Your database is not included in this package.
echo.

if not exist "%ROOT%\Institute_Ledger.py" (echo ERROR: Institute_Ledger.py is missing.& pause & exit /b 1)
if not exist "%ROOT%\app_icon.ico" (echo ERROR: app_icon.ico is missing.& pause & exit /b 1)
if not exist "%ROOT%\assets\background_wallpaper.png" (echo ERROR: shared application wallpaper is missing.& pause & exit /b 1)
if not exist "%ROOT%\assets\fonts\Aptos.ttf" (echo ERROR: supplied Aptos regular font is missing.& pause & exit /b 1)
if not exist "%ROOT%\assets\fonts\Aptos-Bold.ttf" (echo ERROR: supplied Aptos Bold font is missing.& pause & exit /b 1)
if not exist "%ROOT%\assets\fonts\Aptos-SemiBold.ttf" (echo ERROR: supplied Aptos SemiBold font is missing.& pause & exit /b 1)
if not exist "%ROOT%\assets\fonts\Jameel Noori Nastaleeq Regular.ttf" (echo ERROR: supplied Jameel font is missing.& pause & exit /b 1)

set "ISCC="
for %%P in ("%ProgramFiles%\Inno Setup 7\ISCC.exe" "%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe" "%ProgramFiles%\Inno Setup 6\ISCC.exe" "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe") do if exist "%%~P" set "ISCC=%%~P"
if not defined ISCC for /f "delims=" %%I in ('where ISCC.exe 2^>nul') do if not defined ISCC set "ISCC=%%I"
if not defined ISCC (
  echo ERROR: Inno Setup compiler was not found.
  echo It was reported installed, but ISCC.exe could not be located.
  pause
  exit /b 1
)

 echo Checking Python 3.15 64-bit...
py -3.15-64 -c "import sys; print(sys.version); raise SystemExit(0 if sys.maxsize > 2**32 else 1)"
if errorlevel 1 (
  echo ERROR: Python 3.15 64-bit was not found.
  pause
  exit /b 1
)
echo Checking Python 3.15 32-bit...
py -3.15-32 -c "import sys; print(sys.version); raise SystemExit(0 if sys.maxsize <= 2**32 else 1)"
if errorlevel 1 (
  echo ERROR: Python 3.15 32-bit was not found.
  pause
  exit /b 1
)

call :BUILD64
if errorlevel 1 exit /b 1
call :BUILD32
if errorlevel 1 exit /b 1

if not exist "%ROOT%\output" mkdir "%ROOT%\output"
echo.
echo Creating one installer containing the correct EXE for the target architecture...
"%ISCC%" /Qp "%ROOT%\Institute_Ledger_Universal.iss"
if errorlevel 1 (echo ERROR: Inno Setup failed to create installer.& pause & exit /b 1)
if not exist "%ROOT%\output\Institute_Ledger_Setup.exe" (echo ERROR: output installer missing.& pause & exit /b 1)
echo.
echo =============================================================
echo SUCCESS: output\Institute_Ledger_Setup.exe
echo =============================================================
echo One installer for 32-bit or 64-bit Windows.
echo Test first with a COPY of your database, never your only original.
pause
exit /b 0

:BUILD64
echo.
echo Checking existing 64-bit build dependencies (no automatic package upgrades)...
py -3.15-64 -c "import PyInstaller, PIL; print('PyInstaller', PyInstaller.__version__); print('Pillow', PIL.__version__)"
if errorlevel 1 (echo ERROR: PyInstaller and Pillow must already be installed for Python 3.15 64-bit. This script will not upgrade or replace your Python packages.& pause & exit /b 1)
echo Building 64-bit app. Asset source is an absolute path to avoid the spec64\assets failure...
py -3.15-64 -m PyInstaller --noconfirm --clean --windowed --onefile --name "Institute_Ledger_64bit" --distpath "%ROOT%\dist64" --workpath "%ROOT%\build64" --specpath "%ROOT%\spec64" --icon "%ROOT%\app_icon.ico" --add-data "%ROOT%\assets;assets" --exclude-module=fitz --exclude-module=pymupdf --collect-all=PIL "%ROOT%\Institute_Ledger.py"
if errorlevel 1 (echo ERROR: 64-bit EXE build failed. Take a screenshot of this window.& pause & exit /b 1)
if not exist "%ROOT%\dist64\Institute_Ledger_64bit.exe" (echo ERROR: 64-bit EXE missing.& pause & exit /b 1)
exit /b 0

:BUILD32
echo.
echo Checking existing 32-bit build dependencies (no automatic package upgrades)...
py -3.15-32 -c "import PyInstaller, PIL; print('PyInstaller', PyInstaller.__version__); print('Pillow', PIL.__version__)"
if errorlevel 1 (echo ERROR: PyInstaller and Pillow must already be installed for Python 3.15 32-bit. This script will not upgrade or replace your Python packages.& pause & exit /b 1)
echo Building 32-bit app. Asset source is an absolute path...
py -3.15-32 -m PyInstaller --noconfirm --clean --windowed --onefile --name "Institute_Ledger_32bit" --distpath "%ROOT%\dist32" --workpath "%ROOT%\build32" --specpath "%ROOT%\spec32" --icon "%ROOT%\app_icon.ico" --add-data "%ROOT%\assets;assets" --exclude-module=fitz --exclude-module=pymupdf --collect-all=PIL "%ROOT%\Institute_Ledger.py"
if errorlevel 1 (echo ERROR: 32-bit EXE build failed. Take a screenshot of this window.& pause & exit /b 1)
if not exist "%ROOT%\dist32\Institute_Ledger_32bit.exe" (echo ERROR: 32-bit EXE missing.& pause & exit /b 1)
exit /b 0
