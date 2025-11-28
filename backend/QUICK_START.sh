#!/bin/bash
# Alternative setup: Step-by-step manual installation

echo "📋 Manual Backend Setup Instructions"
echo "===================================="
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] && [ ! -f "requirements.txt" ]; then
    echo "❌ Error: This script should be run from the backend directory"
    echo "   Navigate to: live-transcription/backend"
    exit 1
fi

echo "Step 1️⃣  Create Virtual Environment"
echo "-----------------------------------"
echo "Run this command:"
echo "  python3 -m venv .venv"
echo ""
echo "Step 2️⃣  Activate Virtual Environment"
echo "------------------------------------"
echo "On Linux/macOS:"
echo "  source .venv/bin/activate"
echo ""
echo "On Windows:"
echo "  .venv\\Scripts\\activate"
echo ""

echo "Step 3️⃣  Upgrade pip"
echo "-------------------"
echo "Run this command:"
echo "  pip install --upgrade pip"
echo ""

echo "Step 4️⃣  Install Dependencies"
echo "-----------------------------"
echo "Run ONE of these commands:"
echo ""
echo "Option A (using pyproject.toml):"
echo "  pip install -e ."
echo ""
echo "Option B (using requirements.txt):"
echo "  pip install -r requirements.txt"
echo ""

echo "Step 5️⃣  Download NLTK Data"
echo "----------------------------"
echo "Run this command:"
echo "  python setup_nltk.py"
echo ""

echo "Step 6️⃣  Run the Backend"
echo "------------------------"
echo "Run this command:"
echo "  uvicorn app.main:app --reload"
echo ""

echo "✅ Backend will be available at: http://localhost:8000"
