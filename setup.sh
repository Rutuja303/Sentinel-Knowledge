#!/bin/bash

echo "🚀 Setting up AI Knowledge Gap Detector..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OPENAI_API_KEY"
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/documents
mkdir -p data
mkdir -p chroma_db

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OPENAI_API_KEY"
echo "2. Place documents in data/documents/ directory"
echo "3. Run: source venv/bin/activate"
echo "4. Start the API: uvicorn app.main:app --reload"
echo "5. In another terminal, start the dashboard: streamlit run dashboard/app.py"
echo "6. Ingest documents: POST http://localhost:8000/ingest"
