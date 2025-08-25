"""
Ultra-Simple FastAPI Backend for YouTube Video Summarizer Chrome Extension
Minimal version without Pydantic model validation to avoid compatibility issues
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube Video Summarizer API",
    description="Basic YouTube video processing service",
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
        action = request.get('action')
        if action not in ['transcribe', 'summarize']:
            raise HTTPException(status_code=400, detail="Invalid action. Must be 'transcribe' or 'summarize'")
        
        url = request.get('url')
        video_id = request.get('videoId')
        
        if not url or not action or not video_id:
            raise HTTPException(status_code=400, detail="Missing required fields: url, action, videoId")
        
        # Extract video title from URL or use fallback
        video_title = "YouTube Video"
        try:
            # Simple extraction from URL
            if 'youtube.com/watch' in url:
                video_title = f"YouTube Video ID: {video_id}"
        except Exception:
            pass
        
        # Return mock response since we don't have ML models
        if action == 'transcribe':
            result_data = {
                "transcription": f"🎤 Mock transcription for {video_title}\\n\\n"
                               f"This is a demonstration transcription. To get actual video transcription, "
                               f"please install the Whisper AI model.\\n\\n"
                               f"The system detected video ID: {video_id}\\n"
                               f"Source URL: {url}\\n\\n"
                               f"For real transcription functionality, run the full version with AI models installed.",
                "video_info": {
                    "title": video_title,
                    "duration": "Unknown",
                    "url": url,
                    "video_id": video_id
                }
            }
        else:  # summarize
            result_data = {
                "summary": f"📋 Mock summary for {video_title}\\n\\n"
                          f"This is a demonstration summary. To get actual AI-powered video summarization, "
                          f"please install the Llama 2 model.\\n\\n"
                          f"Video Details:\\n"
                          f"• Video ID: {video_id}\\n"
                          f"• Source: YouTube\\n"
                          f"• URL: {url}\\n\\n"
                          f"For real AI summarization, install the required machine learning models.",
                "video_info": {
                    "title": video_title,
                    "duration": "Unknown", 
                    "url": url,
                    "video_id": video_id
                }
            }
        
        processing_time = time.time() - start_time
        
        logger.info(f"Successfully processed video {video_id} in {processing_time:.2f} seconds")
        
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
        "message": "YouTube Video Summarizer API - Working!",
        "status": "running",
        "health": "/health",
        "version": "1.0.0-minimal",
        "endpoints": {
            "health": "GET /health",
            "process": "POST /process-video"
        }
    }

if __name__ == "__main__":
    try:
        import uvicorn
        
        logger.info("🚀 Starting YouTube Video Summarizer Backend (Minimal Mode)")
        logger.info("🌐 Server will be available at: http://localhost:8002")
        logger.info("💡 This is a minimal version for testing the Chrome extension")
        logger.info("🛑 Press Ctrl+C to stop the server")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8002,
            reload=False,
            log_level="info"
        )
    except ImportError:
        logger.error("Uvicorn not found. Please install: pip install uvicorn")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
