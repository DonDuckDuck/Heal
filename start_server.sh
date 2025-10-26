#!/bin/bash

# Start script for Heal backend

echo "🏥 Heal - Diabetes Nutrition Assistant"
echo "======================================"
echo ""

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ ERROR: OPENAI_API_KEY environment variable not set"
    echo "   Please run: export OPENAI_API_KEY='your-api-key'"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo "🚀 Starting FastAPI server..."
echo "   API will be available at http://localhost:8000"
echo "   Docs at http://localhost:8000/docs"
echo ""

# Start the server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

