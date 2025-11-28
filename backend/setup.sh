#!/bin/bash
# Quick setup script for the backend (using global packages)

echo "🚀 Setting up Sales Copilot Backend..."
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Upgrade pip
echo "📥 Upgrading pip..."
pip install --upgrade pip --break-system-packages -q 2>/dev/null
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt --break-system-packages -q 2>/dev/null
echo "✓ Dependencies installed"
echo ""

# Download NLTK data
echo "🧠 Setting up NLTK data..."
python setup_nltk.py
echo ""

echo "✅ Backend setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Configure environment variables in .env file"
echo "2. Run the backend:"
echo "   cd /home/soham-dalvi/Projects/mnse/live-transcription/backend"
echo "   uvicorn app.main:app --reload"
echo ""
echo "🌐 Backend will be available at: http://localhost:8000"
