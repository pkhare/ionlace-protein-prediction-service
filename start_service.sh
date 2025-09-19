#!/bin/bash

# Protein Structure Prediction Service Startup Script

echo "🚀 Starting Protein Structure Prediction Service"
echo "================================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️ Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python3 -c "import fastapi, uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📥 Installing missing dependencies..."
    pip install -r requirements.txt
fi

echo "✅ Dependencies verified"
echo ""
echo "🌐 Starting web service on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the service"
echo ""

# Start the service
python3 app.py
