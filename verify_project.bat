@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python verify_project.py
pause
