@echo off
REM Windows batch file to start the YouTube Summarizer Backend

echo 🎥 YouTube Video Summarizer - Backend Setup
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Show Python version
for /f "tokens=2" %%i in ('python --version') do set python_version=%%i
echo ✅ Python version: %python_version%

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check for model file
set MODEL_FILE=llama-2-7b-32k-instruct.Q4_K_S.gguf
if not exist "%MODEL_FILE%" (
    echo ⚠️  Model file not found: %MODEL_FILE%
    echo 📋 Please download the Llama 2 32K GGUF model from:
    echo    https://huggingface.co/togethercomputer/LLaMA-2-7B-32K-Instruct-GGUF
    echo.
    echo 💡 You can still run the server without the model (transcription will work, summarization will use fallback)
    set /p continue_without_model="🤔 Continue without model? (y/N): "
    
    if /i not "%continue_without_model%"=="y" (
        echo 📋 Please download the model and run the script again.
        pause
        exit /b 1
    )
)

REM Create downloads directory
if not exist "downloads" mkdir downloads

REM Start the server
echo 🚀 Starting FastAPI server...
echo 🌐 Server will be available at: http://localhost:8000
echo 📚 API documentation at: http://localhost:8000/docs
echo.
echo 🛑 Press Ctrl+C to stop the server

python main.py

pause
