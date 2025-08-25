@echo off
echo Starting YouTube Video Summarizer Backend Server...
echo.
echo Server will be available at: http://localhost:8002
echo API documentation at: http://localhost:8002/docs
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
python gemini_server.py

pause
