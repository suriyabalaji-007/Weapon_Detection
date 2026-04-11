@echo off
echo --- Weapon Detection System Setup ---

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.8+ first.
    exit /b
)

:: Check for Virtual Environment
if not exist "venv" (
    echo Creating Virtual Environment...
    python -m venv venv
)

:: Activate Virtual Environment
echo Activating Virtual Environment...
call .\venv\Scripts\activate.bat

:: Check for Dependencies
echo Installing Dependencies (this may take a while)...
pip install -r requirements_updated.txt

:: Final Check
if not exist ".\models\best.pt" (
    echo WARNING: models/best.pt not found. The app will start but detection may fail.
)

:: Run the App
echo Starting Flask Application...
python app.py
pause
