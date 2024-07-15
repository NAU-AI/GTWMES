@echo off
setlocal
REM Change directory to the installation directory
cd /d "%~dp0"
REM Activate virtual environment if needed
REM .\venv\Scripts\activate
REM Run the application with Gunicorn
gunicorn --bind 0.0.0.0:8000 wsgi:app
endlocal
