"""
Ultra-Simple FastAPI Backend for YouTube Video Summarizer Chrome Extension
Minimal version to avoid Pydantic compatibility issues
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
import json
from pytube import YouTube

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube Video Summarizer API",
    description="Simple YouTube video processing service",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Server is running",
        "timestamp": time.time()
    }

@app.post("/process-video")
async def process_video(request: dict):
    """Process video for transcription or summarization"""
    
    start_time = time.time()
    
    try:
        logger.info(f"Processing video: {request.get('videoId')}, action: {request.get('action')}")
        
        # Validate request
        if request.get('action') not in ['transcribe', 'summarize']:
            raise HTTPException(status_code=400, detail="Invalid action. Must be 'transcribe' or 'summarize'")
        
        url = request.get('url')
        action = request.get('action')
        video_id = request.get('videoId')
        
        if not url or not action or not video_id:
            raise HTTPException(status_code=400, detail="Missing required fields: url, action, videoId")
        
        # Get video information
        try:
            yt = YouTube(url)
            video_title = yt.title
            video_length = yt.length
        except Exception as e:
            logger.error(f"Error fetching video info: {e}")
            video_title = "Unknown Video"
            video_length = 0
        
        # Return mock response since we don't have ML models
        if action == 'transcribe':
            result_data = {
                "transcription": f"This is a mock transcription for video: {video_title}. "
                               f"The actual transcription feature requires Whisper model to be installed. "
                               f"Video length: {video_length} seconds. "
                               f"To get real transcription, please install the required AI models.",
                "video_info": {
                    "title": video_title,
                    "duration": video_length,
                    "url": url
                }
            }
        else:  # summarize
            result_data = {
                "summary": f"This is a mock summary for video: {video_title}. "
                          f"The actual summarization feature requires Llama model to be installed. "
                          f"Video appears to be {video_length} seconds long. "
                          f"To get real AI-powered summarization, please install the required models.",
                "video_info": {
                    "title": video_title,
                    "duration": video_length,
                    "url": url
                }
            }
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "data": result_data,
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        return {
            "success": False,
            "error": f"Error processing video: {str(e)}"
        }

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
    
    logger.info("🚀 Starting YouTube Video Summarizer Backend (Ultra-Simple Mode)")
    logger.info("🌐 Server will be available at: http://localhost:8001")
    logger.info("📚 API documentation at: http://localhost:8001/docs")
    logger.info("💡 This is a simplified version without AI models")
    logger.info("🛑 Press Ctrl+C to stop the server")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=False,  # Disable reload to avoid issues
        log_level="info"
    )
