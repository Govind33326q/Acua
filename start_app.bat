@echo off
cd /d "D:\AquaVisionaries\AquaVisinaries\AquaVisinaries"
set "VITE_API_URL=http://127.0.0.1:8001"
set "CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:5175,http://127.0.0.1:5175"

where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed or not on PATH.
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    C:\Users\govin\AppData\Local\Programs\Python\Python312\python.exe -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

start "AquaScan Backend" cmd /k "cd /d ""D:\AquaVisionaries\AquaVisinaries\AquaVisinaries"" && call .venv\Scripts\activate.bat && python -m uvicorn src.api:app --host 127.0.0.1 --port 8001"

cd frontend
set "PATH=C:\Program Files\nodejs;%PATH%"
if not exist "node_modules" (
    echo Installing frontend dependencies...
    "C:\Program Files\nodejs\npm.cmd" install
)
start "AquaScan Frontend" cmd /k "cd /d ""D:\AquaVisionaries\AquaVisinaries\AquaVisinaries\frontend"" && set "VITE_API_URL=http://127.0.0.1:8001" && "C:\Program Files\nodejs\npm.cmd" run dev -- --host 127.0.0.1 --port 5174 --strictPort"

cd /d "D:\AquaVisionaries\AquaVisinaries\AquaVisinaries"
printf "Backend and frontend startup commands launched.\n"
printf "Open http://127.0.0.1:5174/\n"
