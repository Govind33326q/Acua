@echo off
rem AquaVisionaries - one-window start (Windows). Run from any folder.
setlocal
cd /d "%~dp0"
set "PORT=8001"

where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment with %PY% ...
    %PY% -m venv .venv || (echo Python 3.12 was not found. Install it from python.org and tick "Add to PATH". & pause & exit /b 1)
    call .venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt || (echo Dependency installation failed. & pause & exit /b 1)
) else (
    call .venv\Scripts\activate.bat
)

if not exist "frontend\dist\index.html" (
    echo The built interface frontend\dist is missing. Build it with: cd frontend ^&^& npm install ^&^& npm run build
    pause & exit /b 1
)

echo.
echo AquaVisionaries is starting on http://127.0.0.1:%PORT%/
echo Keep this window open. Press Ctrl+C to stop.
start "" "http://127.0.0.1:%PORT%/"
python -m uvicorn src.api:app --host 127.0.0.1 --port %PORT%
