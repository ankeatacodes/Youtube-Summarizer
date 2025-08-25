"""
Simple FastAPI Backend for YouTube Video Summarizer Chrome Extension
A lightweight version that works without heavy ML dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Union
import logging
import time
import os
from pathlib import Path
import requests
from pytube import YouTube

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube Video Summarizer API (Simple)",
    description="Lightweight YouTube video transcription service",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class VideoProcessRequest(BaseModel):
    url: str
    action: str  # 'summarize' or 'transcribe'
    videoId: str

class ProcessResponse(BaseModel):
    success: bool
    data: Union[Dict[str, Any], None] = None
    error: Union[str, None] = None

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: float

# Configuration
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Server is running",
        timestamp=time.time()
    )

@app.post("/process-video", response_model=ProcessResponse)
async def process_video(request: VideoProcessRequest):
    """Process video for transcription or summarization"""
    
    start_time = time.time()
    
    try:
        logger.info(f"Processing video: {request.videoId}, action: {request.action}")
        
        # Validate request
        if request.action not in ['transcribe', 'summarize']:
            raise HTTPException(status_code=400, detail="Invalid action. Must be 'transcribe' or 'summarize'")
        
        # Get video information
        try:
            yt = YouTube(request.url)
            video_title = yt.title
            video_length = yt.length
        except Exception as e:
            logger.error(f"Error fetching video info: {e}")
            video_title = "Unknown"
            video_length = 0
        
        # For now, return a mock response since we don't have the ML models
        if request.action == 'transcribe':
            result_data = {
                "transcription": f"This is a mock transcription for video: {video_title}. "
                               f"The actual transcription feature requires Whisper model to be installed. "
                               f"Video length: {video_length} seconds.",
                "video_info": {
                    "title": video_title,
                    "duration": video_length,
                    "url": request.url
                }
            }
        else:  # summarize
            result_data = {
                "summary": f"This is a mock summary for video: {video_title}. "
                          f"The actual summarization feature requires Llama model to be installed. "
                          f"To get real transcription and summarization, please install the required models.",
                "video_info": {
                    "title": video_title,
                    "duration": video_length,
                    "url": request.url
                }
            }
        
        processing_time = time.time() - start_time
        
        return ProcessResponse(
            success=True,
            data=result_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        return ProcessResponse(
            success=False,
            error=f"Error processing video: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "YouTube Video Summarizer API",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting YouTube Video Summarizer Backend (Simple Mode)")
    logger.info("🌐 Server will be available at: http://localhost:8000")
    logger.info("📚 API documentation at: http://localhost:8000/docs")
    logger.info("💡 This is a simplified version without AI models")
    logger.info("🛑 Press Ctrl+C to stop the server")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
