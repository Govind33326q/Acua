@echo off
rem Streamlit variant of the detector (upload + whole/tiled detection).
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (echo Run start_app.bat once first to create the environment. & pause & exit /b 1)
call .venv\Scripts\activate.bat
cd Aqua-Scan
python -m streamlit run app.py
