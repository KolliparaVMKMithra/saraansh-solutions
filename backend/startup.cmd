@echo off
REM Startup script for Flask app on Azure App Service

echo Starting Python dependencies installation...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Starting Flask application...
waitress-serve --port=%PORT% --host=0.0.0.0 app:app
