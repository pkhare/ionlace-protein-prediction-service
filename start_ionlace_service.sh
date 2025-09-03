#!/bin/bash

# Ionlace Protein Structure Prediction Service Startup Script
# This script ensures the correct conda environment is activated

echo "🚀 Starting Ionlace Protein Structure Prediction Service"
echo "========================================================"

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed or not in PATH"
    echo "Please install Anaconda or Miniconda first"
    exit 1
fi

# Check if the ionlace-env exists
if ! conda env list | grep -q "ionlace-env"; then
    echo "❌ ionlace-env not found. Creating it now..."
    conda create -n ionlace-env python=3.9 -y
    echo "📦 Installing dependencies..."
    conda activate ionlace-env
    pip install -r requirements.txt
else
    echo "📦 Activating ionlace-env environment..."
    conda activate ionlace-env
fi

# Verify we're in the right environment
if [[ "$CONDA_DEFAULT_ENV" != "ionlace-env" ]]; then
    echo "❌ Failed to activate ionlace-env environment"
    exit 1
fi

echo "✅ Environment: $CONDA_DEFAULT_ENV"
echo "🐍 Python: $(which python)"
echo "📚 Python version: $(python --version)"

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python -c "
import fastapi, uvicorn, torch, transformers, Bio
print('✅ All core dependencies available')
" || {
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
}

echo "🌐 Starting web service on http://localhost:8000"
echo "📖 API documentation will be available at http://localhost:8000/docs"
echo "🔄 Press Ctrl+C to stop the service"
echo ""

# Start the service
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
