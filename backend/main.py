"""
FastAPI Backend for YouTube Video Summarizer Chrome Extension
Converts the original Streamlit app into a REST API service
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
import logging
import asyncio
import time
import os
from pathlib import Path

# Import the existing functionality
from pytube import YouTube
from haystack.nodes import PromptNode, PromptModel
from haystack.nodes.audio import WhisperTranscriber
from haystack.pipelines import Pipeline

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube Video Summarizer API",
    description="AI-powered YouTube video transcription and summarization using Llama 2",
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
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: float

# Global variables for model initialization
model = None
prompt_node = None
whisper = None
pipeline = None

# Configuration
MODEL_PATH = "llama-2-7b-32k-instruct.Q4_K_S.gguf"
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

async def initialize_ai_models():
    """Initialize AI models on startup"""
    global model, prompt_node, whisper, pipeline
    
    try:
        logger.info("Initializing AI models...")
        
        # Check if model file exists
        if not os.path.exists(MODEL_PATH):
            logger.warning(f"Model file not found: {MODEL_PATH}")
            logger.info("Please download the Llama 2 model and place it in the backend directory")
            return False
        
        # Initialize Whisper
        whisper = WhisperTranscriber()
        logger.info("Whisper transcriber initialized")
        
        # Initialize Llama model
        try:
            from model_add import LlamaCPPInvocationLayer
            model = PromptModel(
                model_name_or_path=MODEL_PATH,
                invocation_layer_class=LlamaCPPInvocationLayer,
                use_gpu=False,
                max_length=512
            )
            
            summary_prompt = "deepset/summarization"
            prompt_node = PromptNode(
                model_name_or_path=model, 
                default_prompt_template=summary_prompt, 
                use_gpu=False
            )
            logger.info("Llama 2 model initialized")
        except Exception as e:
            logger.warning(f"Could not initialize Llama 2 model: {e}")
            logger.info("Summarization will use fallback method")
        
        # Create pipeline
        pipeline = Pipeline()
        pipeline.add_node(component=whisper, name="whisper", inputs=["File"])
        if prompt_node:
            pipeline.add_node(component=prompt_node, name="prompt", inputs=["whisper"])
        
        logger.info("AI models initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing AI models: {str(e)}")
        return False

def download_youtube_audio(url: str) -> str:
    """Download audio from YouTube video"""
    try:
        logger.info(f"Downloading audio from: {url}")
        yt = YouTube(url)
        
        # Get the best audio stream
        audio_stream = yt.streams.filter(only_audio=True).first()
        if not audio_stream:
            # Fallback to video stream with audio
            audio_stream = yt.streams.filter(abr='160kbps').last()
        
        if not audio_stream:
            raise HTTPException(status_code=400, detail="No suitable audio stream found")
        
        # Download to downloads directory
        file_path = audio_stream.download(output_path=DOWNLOAD_DIR)
        logger.info(f"Audio downloaded: {file_path}")
        
        return file_path
        
    except Exception as e:
        logger.error(f"Error downloading audio: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to download audio: {str(e)}")

def transcribe_audio(file_path: str) -> str:
    """Transcribe audio file using Whisper"""
    try:
        logger.info(f"Transcribing audio: {file_path}")
        
        if whisper is None:
            raise HTTPException(status_code=500, detail="Whisper not initialized")
        
        # Create a simple pipeline with just Whisper for transcription
        transcribe_pipeline = Pipeline()
        transcribe_pipeline.add_node(component=whisper, name="whisper", inputs=["File"])
        
        output = transcribe_pipeline.run(file_paths=[file_path])
        transcription = output["documents"][0].content if output.get("documents") else ""
        
        logger.info("Transcription completed")
        return transcription
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

def summarize_text(text: str) -> str:
    """Summarize text using Llama 2 or fallback method"""
    try:
        logger.info("Summarizing text...")
        
        # Try to use the full pipeline if available
        if prompt_node and pipeline:
            try:
                # Use the full Haystack pipeline with Llama 2
                temp_file = DOWNLOAD_DIR / "temp_transcript.txt"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                output = pipeline.run(file_paths=[str(temp_file)])
                
                # Clean up temp file
                temp_file.unlink(missing_ok=True)
                
                if output.get("results"):
                    summary = output["results"][0].split("\n\n[INST]")[0]
                    logger.info("Summary generated using Llama 2")
                    return summary
            except Exception as e:
                logger.warning(f"Llama 2 summarization failed: {e}")
        
        # Fallback to extractive summarization
        sentences = text.split('. ')
        if len(sentences) > 5:
            # Take first 3 and last 2 sentences for a better summary
            summary_sentences = sentences[:3] + sentences[-2:]
            summary = '. '.join(summary_sentences)
            if not summary.endswith('.'):
                summary += '.'
        else:
            summary = text
        
        # Add a note about the summarization method
        if not (prompt_node and pipeline):
            summary = f"[Extractive Summary - Install Llama 2 model for AI summarization]\n\n{summary}"
        
        logger.info("Summary generated using fallback method")
        return summary
        
    except Exception as e:
        logger.error(f"Error summarizing text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

async def cleanup_file(file_path: str):
    """Clean up downloaded file after processing"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up file: {file_path}")
    except Exception as e:
        logger.warning(f"Error cleaning up file {file_path}: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    success = await initialize_ai_models()
    if not success:
        logger.warning("Some AI models failed to initialize - check model files")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="YouTube Summarizer API is running",
        timestamp=time.time()
    )

@app.post("/process-video", response_model=ProcessResponse)
async def process_video(
    request: VideoProcessRequest, 
    background_tasks: BackgroundTasks
):
    """Process YouTube video for transcription and/or summarization"""
    start_time = time.time()
    
    try:
        logger.info(f"Processing video: {request.url} (action: {request.action})")
        
        # Download audio
        file_path = download_youtube_audio(request.url)
        
        # Schedule cleanup
        background_tasks.add_task(cleanup_file, file_path)
        
        # Transcribe audio
        transcription = transcribe_audio(file_path)
        
        result = {
            "transcription": transcription,
            "video_id": request.videoId,
            "action": request.action
        }
        
        # If summarization is requested, add summary
        if request.action == "summarize":
            summary = summarize_text(transcription)
            result["summary"] = summary
        
        processing_time = time.time() - start_time
        
        logger.info(f"Video processing completed in {processing_time:.2f} seconds")
        
        return ProcessResponse(
            success=True,
            data=result,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/models/status")
async def get_models_status():
    """Get status of AI models"""
    return {
        "whisper": whisper is not None,
        "llama": model is not None,
        "prompt_node": prompt_node is not None,
        "pipeline": pipeline is not None,
        "model_path_exists": os.path.exists(MODEL_PATH)
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "YouTube Video Summarizer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
