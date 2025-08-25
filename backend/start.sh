#!/bin/bash

# Startup script for YouTube Summarizer Backend
# This script sets up the environment and starts the FastAPI server

echo "🎥 YouTube Video Summarizer - Backend Setup"
echo "=========================================="

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Download model if it doesn't exist
MODEL_FILE="llama-2-7b-32k-instruct.Q4_K_S.gguf"
if [ ! -f "$MODEL_FILE" ]; then
    echo "⚠️  Model file not found: $MODEL_FILE"
    echo "📋 Please download the Llama 2 32K GGUF model from:"
    echo "   https://huggingface.co/togethercomputer/LLaMA-2-7B-32K-Instruct-GGUF"
    echo ""
    echo "💡 You can still run the server without the model (transcription will work, summarization will use fallback)"
    read -p "🤔 Continue without model? (y/N): " continue_without_model
    
    if [[ ! $continue_without_model =~ ^[Yy]$ ]]; then
        echo "📋 Please download the model and run the script again."
        exit 1
    fi
fi

# Create downloads directory
mkdir -p downloads

# Start the server
echo "🚀 Starting FastAPI server..."
echo "🌐 Server will be available at: http://localhost:8000"
echo "📚 API documentation at: http://localhost:8000/docs"
echo ""
echo "🛑 Press Ctrl+C to stop the server"

python main.py
