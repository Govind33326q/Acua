@echo off
cd /d "D:\AquaVisionaries\AquaVisinaries\AquaVisinaries"
call .venv\Scripts\activate.bat
python -c "import sys; sys.path.insert(0, r'D:\AquaVisionaries\AquaVisinaries\AquaVisinaries'); import src.api; print('BACKEND_IMPORT_OK')"
cd frontend
set "PATH=C:\Program Files\nodejs;%PATH%"
call npm run build
if errorlevel 1 (
    echo VERIFY_FAILED
    exit /b 1
)
echo VERIFY_OK
