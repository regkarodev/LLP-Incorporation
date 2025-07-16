@echo off

rem LLP Incorporation Automation API Deployment Script for Windows

echo 🚀 Starting LLP Automation API Deployment...

rem Set environment variables for production
set FLASK_DEBUG=false
set FLASK_HOST=0.0.0.0
set FLASK_PORT=8009

rem Create logs directory
if not exist "logs" mkdir logs

rem Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

rem Install Playwright browsers
echo 🌐 Installing Playwright browsers...
playwright install

rem Run with Waitress (Cross-platform)
echo 🏃 Starting with Waitress...
waitress-serve --host=0.0.0.0 --port=8009 api_main:app

rem Alternative: For development, use Flask dev server
rem echo 🏃 Starting with Flask dev server...
rem python api_main.py

pause 