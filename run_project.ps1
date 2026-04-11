# Weapon Detection System Runner Script

Write-Host "--- Weapon Detection System Setup ---" -ForegroundColor Cyan

# Check for Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed. Please install Python 3.8+ first."
    exit
}

# Check for Virtual Environment
if (!(Test-Path ".\venv")) {
    Write-Host "Creating Virtual Environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate Virtual Environment
Write-Host "Activating Virtual Environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Check for Dependencies
Write-Host "Installing Dependencies (this may take a while)..." -ForegroundColor Yellow
pip install -r requirements_updated.txt

# Final Check
if (!(Test-Path ".\models\best.pt")) {
    Write-Host "WARNING: models/best.pt not found. The app will start but detection may fail." -ForegroundColor Red
}

# Run the App
Write-Host "Starting Flask Application..." -ForegroundColor Green
python app.py
