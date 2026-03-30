@echo off
title BG Eraser — Installer
color 0A

echo.
echo  =============================================
echo   BG ERASER — Offline Background Remover
echo   Auto Installer for Windows
echo  =============================================
echo.

:: Check Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo  [ERROR] Python not found! Please install Python 3.10+
    echo  Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo  [OK] Python detected.

:: Create virtual environment
echo  [1/4] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

:: Upgrade pip
echo  [2/4] Upgrading pip...
python -m pip install --upgrade pip --quiet

:: Install dependencies
echo  [3/4] Installing dependencies (this may take a few minutes)...
pip install -r requirements.txt --quiet

:: Pre-download the U2Net model
echo  [4/4] Pre-downloading AI model (U2Net ~170MB, one-time only)...
python -c "from rembg import remove; from PIL import Image; import io; img=Image.new('RGB',(10,10)); buf=io.BytesIO(); img.save(buf,format='PNG'); remove(buf.getvalue())" 2>nul
echo  [OK] Model ready.

echo.
echo  =============================================
echo   Installation complete!
echo   Run 'run.bat' to launch the app.
echo  =============================================
echo.
pause
