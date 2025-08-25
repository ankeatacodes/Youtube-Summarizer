"""
Enhanced Gemini AI-powered FastAPI Backend with Improved Transcript Extraction
Addresses common issues with pytube and youtube-transcript-api
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Union
import logging
import time
import os
import re
import google.generativeai as genai
from improved_transcript_extractor import transcript_extractor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini AI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to get API key from environment, fallback to hardcoded (for demo)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCB3SQilhWPslMmVFdV9Lz_67AHK2E_Rd4")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI(
    title="YouTube Video Summarizer API (Enhanced Gemini AI)",
    description="AI-powered YouTube video transcription and summarization service with improved transcript extraction",
    version="2.1.0"
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

class TestGeminiResponse(BaseModel):
    success: bool
    message: str
    summary: Union[str, None] = None
    error: Union[str, None] = None
    timestamp: float

def extract_video_id(url):
    """Extract video ID from YouTube URL"""
    return transcript_extractor.extract_video_id(url)

def get_video_info(url):
    """Get video information using improved extraction methods"""
    return transcript_extractor.get_video_info_robust(url)

def get_video_transcript(url):
    """Extract transcript using improved methods"""
    return transcript_extractor.get_transcript_robust(url)

def chunk_text(text, max_tokens=2000):
    """Split text into chunks for processing by LLM"""
    if not text:
        return []
    
    # Rough estimation: 1 token ≈ 4 characters
    max_chars = max_tokens * 4
    
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    sentences = re.split(r'[.!?]+', text)
    
    current_chunk = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # If adding this sentence would exceed the limit, save current chunk
        if len(current_chunk) + len(sentence) > max_chars and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            if current_chunk:
                current_chunk += ". " + sentence
            else:
                current_chunk = sentence
    
    # Add the last chunk if it exists
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    logger.info(f"Split text into {len(chunks)} chunks")
    return chunks

def summarize_chunk(chunk, video_info, chunk_num, total_chunks):
    """Summarize a single chunk of transcript"""
    try:
        prompt = f"""
You are analyzing part {chunk_num} of {total_chunks} from a YouTube video transcript. 
Create a natural summary of this section as if you're telling a friend what happened in this part.

Video: "{video_info['title']}" by {video_info['author']}

Transcript section:
{chunk}

Write a conversational summary of this section. Focus on:
- Key points discussed in this part
- Important information or insights shared
- Any interesting details or examples mentioned
- How this section contributes to the overall video

Keep it natural and flowing, like you're explaining what you just heard to someone.
"""
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        logger.error(f"Error summarizing chunk {chunk_num}: {str(e)}")
        return f"Error summarizing section {chunk_num}: {str(e)}"

def create_final_summary(chunk_summaries, video_info):
    """Combine chunk summaries into a final cohesive summary"""
    try:
        combined_summaries = "\\n\\n".join([f"Section {i+1}: {summary}" for i, summary in enumerate(chunk_summaries)])
        
        prompt = f"""
You are creating a final, cohesive summary from multiple section summaries of a YouTube video.
Write this as if you watched the entire video and are now telling a friend what it's about.

Video: "{video_info['title']}" by {video_info['author']}
Duration: {video_info.get('length', 'Unknown')} seconds

Section summaries:
{combined_summaries}

Create a natural, flowing summary that:
1. Captures the main theme and purpose of the video
2. Highlights the most interesting or valuable points
3. Explains what viewers will learn or gain from watching
4. Feels conversational and engaging, not robotic

Write in flowing paragraphs without bullet points. Make it sound like you genuinely watched this video and found it interesting enough to recommend to a friend.
"""
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        logger.error(f"Error creating final summary: {str(e)}")
        return f"Error creating final summary: {str(e)}"

def generate_summary_with_gemini(video_info, action="summarize", url=None):
    """Generate natural, user-friendly summary using Gemini AI with improved transcript extraction"""
    try:
        # First, try to get the actual transcript using improved methods
        transcript = None
        transcript_source = "none"
        
        if url:
            logger.info("🔍 Attempting improved transcript extraction...")
            transcript = get_video_transcript(url)
            if transcript:
                transcript_source = "extracted"
                logger.info(f"✅ Successfully extracted transcript: {len(transcript)} characters")
            else:
                logger.warning("⚠️ No transcript could be extracted with any method")
        
        if action == "summarize":
            if transcript and len(transcript.strip()) > 100:
                logger.info(f"📝 Using actual transcript for summarization ({len(transcript)} characters)")
                
                # Check if transcript needs chunking
                chunks = chunk_text(transcript, max_tokens=2000)
                
                if len(chunks) == 1:
                    # Short video, summarize directly
                    duration_text = f"{video_info['length']} seconds" if video_info['length'] != "Unknown" else "Unknown duration"
                    
                    prompt = f"""
You are an AI assistant that creates natural, human-like summaries of YouTube videos. 
You have the actual transcript and should write as if you watched the video yourself.

Video Information:
- Title: {video_info['title']}
- Creator: {video_info['author']}
- Duration: {duration_text}
- Views: {video_info['views']}
- Published: {video_info['publish_date']}

Full Transcript:
{transcript}

Instructions:
Write a conversational summary in flowing paragraphs (not bullet points) that covers:
- What the video is mainly about (topic/theme)
- The most interesting or useful points from the actual content
- Key insights, concepts, or takeaways for the viewer
- If educational, what viewers will learn; if entertainment, what makes it engaging

Write naturally as if you're telling a friend about this video you just watched. 
Avoid generic phrases like "This video discusses..." - instead, narrate what actually happens.
Include specific details and examples from the transcript to make it engaging.
"""
                    
                    response = model.generate_content(prompt)
                    return f"📋 **Based on actual video transcript:**\\n\\n{response.text}"
                
                else:
                    # Long video, use chunking approach
                    logger.info(f"📚 Long video detected, processing {len(chunks)} chunks...")
                    
                    chunk_summaries = []
                    for i, chunk in enumerate(chunks):
                        logger.info(f"⚙️ Processing chunk {i+1}/{len(chunks)}")
                        chunk_summary = summarize_chunk(chunk, video_info, i+1, len(chunks))
                        chunk_summaries.append(chunk_summary)
                        
                        # Add a small delay to avoid rate limiting
                        time.sleep(0.5)
                    
                    # Create final cohesive summary
                    final_summary = create_final_summary(chunk_summaries, video_info)
                    return f"📋 **Based on actual video transcript:**\\n\\n{final_summary}"
            
            else:
                # Fallback to metadata-based summary
                logger.warning("🔄 No transcript available, falling back to metadata-based analysis")
                duration_text = f"{video_info['length']} seconds" if video_info['length'] != "Unknown" else "Unknown duration"
                
                # Check if we have meaningful metadata
                has_real_title = not video_info['title'].startswith("YouTube Video (ID:")
                has_description = video_info['description'] and not video_info['description'].startswith("Unable to retrieve")
                
                if has_real_title or has_description:
                    # We have some meaningful data
                    prompt = f"""
You are an AI assistant that creates natural, human-like summaries of YouTube videos. 
The transcript isn't available, so base your summary on the video metadata.

Video Information:
- Title: {video_info['title']}
- Creator: {video_info['author']}
- Duration: {duration_text}
- Views: {video_info['views']}
- Published: {video_info['publish_date']}
- Description: {video_info['description']}

Instructions:
Write a conversational summary in flowing paragraphs based on the available information.
Explain what the video likely covers and why someone might want to watch it.
Be honest that you're working from the title and description, but make it engaging.
Write naturally as if you're recommending this video to a friend based on what you know about it.
"""
                    
                    response = model.generate_content(prompt)
                    return f"📝 **Based on video metadata (transcript not available):**\\n\\n{response.text}\\n\\n💡 *Note: This summary is based on the video title and description. For more detailed insights, try watching the video directly.*"
                
                else:
                    # Very minimal data - provide a helpful response
                    video_id = extract_video_id(url) if url else "unknown"
                    return f"""🚫 **Limited Information Available**

I'm having trouble accessing detailed information about this YouTube video (ID: {video_id}) due to current API restrictions and privacy settings.

**What this means:**
- The video's transcript/captions aren't publicly accessible
- Basic metadata (title, description) couldn't be retrieved
- This could be due to privacy settings, regional restrictions, or recent YouTube policy changes

**What you can try instead:**
1. **Direct viewing**: Watch the first 30-60 seconds to get a feel for the content
2. **Community insights**: Check the video's comments for viewer perspectives
3. **Channel context**: Look at the creator's other videos to understand their content style
4. **Video chapters**: If available, use timestamps/chapters to navigate to relevant sections

**Technical note**: YouTube has implemented stricter access controls that limit automated transcript extraction. This affects many AI tools, not just this one.

I apologize that I can't provide the detailed summary you're looking for. The video may still be valuable - it just requires direct viewing to appreciate its content."""
                
        else:  # transcribe
            if transcript and len(transcript.strip()) > 100:
                # For transcribe action, return the cleaned transcript with some context
                duration_text = f"{video_info['length']} seconds" if video_info['length'] != "Unknown" else "Unknown duration"
                
                prompt = f"""
You have the transcript of a YouTube video. Present it in a natural, readable format with some context.

Video: "{video_info['title']}" by {video_info['author']} ({duration_text})

Raw Transcript:
{transcript}

Clean up this transcript and present it in a readable format. Add paragraph breaks where appropriate, 
fix obvious transcription errors, and make it flow naturally. Keep all the content but make it easier to read.
Add brief section headers if you notice distinct topics being discussed.
"""
                
                response = model.generate_content(prompt)
                return f"📄 **Video Transcript:**\\n\\n{response.text}"
            else:
                # Fallback for transcribe when no transcript available
                logger.warning("❌ No transcript available for transcription request")
                return """📄 **Transcript Not Available**

Unfortunately, I couldn't extract a transcript for this video. This could be due to several reasons:

**Possible causes:**
- The video doesn't have captions or subtitles enabled
- Captions are not in English or are auto-generated poorly
- The video has privacy restrictions that prevent transcript access
- Recent YouTube API changes that limit automated access

**Alternatives:**
1. **YouTube's built-in captions**: Try turning on captions directly in the YouTube player (CC button)
2. **Manual transcription**: Consider using YouTube's auto-generated captions as a starting point
3. **Third-party tools**: Some browser extensions can help extract captions when they exist
4. **Summary instead**: Try using the 'summarize' option, which works with video metadata

**Tip**: If this is your own video, you can add captions through YouTube Studio, which will make future transcript requests possible."""

    except Exception as e:
        logger.error(f"Error generating content with Gemini: {str(e)}")
        return f"❌ **Error generating AI analysis:** {str(e)}\\n\\nPlease check your Gemini API key and internet connection. If the problem persists, this might be due to YouTube access restrictions."

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Enhanced Gemini AI Server is running with improved transcript extraction",
        timestamp=time.time()
    )

@app.post("/process-video", response_model=ProcessResponse)
async def process_video(request: VideoProcessRequest):
    """Process video for transcription or summarization using enhanced Gemini AI"""
    
    start_time = time.time()
    
    try:
        logger.info(f"🎯 Processing video: {request.videoId}, action: {request.action}")
        
        # Validate request
        if request.action not in ['transcribe', 'summarize']:
            raise HTTPException(status_code=400, detail="Invalid action. Must be 'transcribe' or 'summarize'")
        
        # Extract video ID and validate URL
        video_id = extract_video_id(request.url)
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        # Get video information using improved methods
        logger.info("📊 Extracting video information...")
        video_info = get_video_info(request.url)
        
        # Generate AI content using Gemini with improved transcript extraction
        logger.info("🤖 Generating AI content...")
        ai_content = generate_summary_with_gemini(video_info, request.action, request.url)
        
        # Prepare response based on action
        if request.action == 'transcribe':
            result_data = {
                "transcription": ai_content,
                "video_info": {
                    "title": video_info['title'],
                    "duration": f"{video_info['length']} seconds" if video_info['length'] != "Unknown" else "Unknown",
                    "url": request.url,
                    "video_id": video_id,
                    "author": video_info['author'],
                    "views": video_info['views'],
                    "source": video_info.get('source', 'unknown')
                }
            }
        else:  # summarize
            result_data = {
                "summary": ai_content,
                "video_info": {
                    "title": video_info['title'],
                    "duration": f"{video_info['length']} seconds" if video_info['length'] != "Unknown" else "Unknown", 
                    "url": request.url,
                    "video_id": video_id,
                    "author": video_info['author'],
                    "views": video_info['views'],
                    "publish_date": video_info['publish_date'],
                    "source": video_info.get('source', 'unknown')
                }
            }
        
        processing_time = time.time() - start_time
        
        logger.info(f"✅ Successfully processed video {video_id} in {processing_time:.2f} seconds")
        
        return ProcessResponse(
            success=True,
            data=result_data,
            error=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing video: {str(e)}")
        processing_time = time.time() - start_time
        return ProcessResponse(
            success=False,
            data=None,
            error=f"Error processing video: {str(e)}"
        )

@app.post("/test-gemini", response_model=TestGeminiResponse)
async def test_gemini():
    """Test endpoint to verify Gemini AI integration"""
    try:
        response = model.generate_content("Hey! I'm testing if you're working properly. Can you give me a friendly, natural response confirming everything is working great?")
        return TestGeminiResponse(
            success=True,
            message="Gemini AI is working properly",
            summary=response.text,
            error=None,
            timestamp=time.time()
        )
    except Exception as e:
        return TestGeminiResponse(
            success=False,
            message="Gemini AI test failed",
            summary=None,
            error=str(e),
            timestamp=time.time()
        )

@app.post("/test-transcript")
async def test_transcript_extraction():
    """Test endpoint for transcript extraction with various URLs"""
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Popular video with captions
        "https://www.youtube.com/watch?v=bUAYvKCFpTg",  # Previous test video
    ]
    
    results = {}
    for url in test_urls:
        try:
            video_id = extract_video_id(url)
            logger.info(f"Testing transcript extraction for {video_id}")
            
            # Test video info extraction
            video_info = get_video_info(url)
            
            # Test transcript extraction
            transcript = get_video_transcript(url)
            
            results[video_id] = {
                "video_info": video_info,
                "transcript_available": transcript is not None,
                "transcript_length": len(transcript) if transcript else 0,
                "transcript_preview": transcript[:200] + "..." if transcript and len(transcript) > 200 else transcript
            }
            
        except Exception as e:
            results[url] = {"error": str(e)}
    
    return {
        "test_results": results,
        "timestamp": time.time()
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "YouTube Video Summarizer API - Enhanced Gemini AI Powered",
        "status": "running",
        "ai_model": "Google Gemini 1.5 Flash",
        "features": [
            "Improved transcript extraction",
            "Multiple fallback methods",
            "Better error handling",
            "Enhanced video info extraction"
        ],
        "docs": "/docs",
        "health": "/health",
        "version": "2.1.0-enhanced"
    }

if __name__ == "__main__":
    try:
        import uvicorn
        
        logger.info("🚀 Starting Enhanced YouTube Video Summarizer Backend")
        logger.info("🌐 Server will be available at: http://localhost:8002")
        logger.info("📚 API documentation at: http://localhost:8002/docs")
        logger.info("🧠 Powered by Google Gemini 1.5 Flash")
        logger.info("⚡ Enhanced with improved transcript extraction")
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
