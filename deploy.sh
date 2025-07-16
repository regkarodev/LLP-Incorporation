#!/bin/bash

# LLP Incorporation Automation API Deployment Script

echo "🚀 Starting LLP Automation API Deployment..."

# Set environment variables for production
export FLASK_DEBUG=false
export FLASK_HOST=0.0.0.0
export FLASK_PORT=8009

# Create logs directory
mkdir -p logs

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install

# Run with Gunicorn (Linux/Mac)
echo "🏃 Starting with Gunicorn..."
gunicorn --config gunicorn_config.py api_main:app

# Alternative: Run with Waitress (Cross-platform)
# echo "🏃 Starting with Waitress..."
# waitress-serve --host=0.0.0.0 --port=8009 api_main:app

# For development, use Flask dev server
# echo "🏃 Starting with Flask dev server..."
# python api_main.py 