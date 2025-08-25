"""
Gemini AI-powered FastAPI Backend for YouTube Video Summarizer Chrome Extension
Integrates with Google's Gemini AI for real video summarization
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Union
import logging
import time
import os
import re
import xml.etree.ElementTree as ET
import google.generativeai as genai
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import math
from xml.etree import ElementTree as ET

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini AI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to get API key from environment, fallback to hardcoded (for demo)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCB3SQilhWPslMmVFdV9Lz_67AHK2E_Rd4")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI(
    title="YouTube Video Summarizer API (Gemini AI)",
    description="AI-powered YouTube video transcription and summarization service using Google Gemini",
    version="2.0.0"
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
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_video_info_from_api(video_id):
    """Try to get video info using YouTube Data API v3 (if API key available)"""
    try:
        # You can add your YouTube Data API v3 key here
        # YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
        # if YOUTUBE_API_KEY:
        #     ... implement YouTube Data API v3 call
        
        # For now, return None to indicate no API available
        return None
    except Exception as e:
        logger.warning(f"YouTube Data API failed: {str(e)}")
        return None

def get_video_info_from_webpage(url):
    """Try to extract basic info from YouTube webpage"""
    try:
        import re
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # Try to extract title from page title or JSON-LD
            title_match = re.search(r'<title>([^<]+)</title>', content)
            if title_match:
                title = title_match.group(1).replace(' - YouTube', '').strip()
                if title and title != 'YouTube':
                    return {
                        "title": title,
                        "description": "Description extracted from webpage metadata",
                        "length": "Unknown",
                        "views": "Unknown",
                        "author": "Unknown",
                        "publish_date": "Unknown",
                        "source": "webpage"
                    }
        
        return None
    except Exception as e:
        logger.warning(f"Webpage extraction failed: {str(e)}")
        return None

def get_video_info(url):
    """Get video information using multiple methods"""
    video_id = extract_video_id(url)
    
    # Method 1: Try pytube
    try:
        yt = YouTube(url)
        return {
            "title": yt.title,
            "description": yt.description[:1000] + "..." if yt.description and len(yt.description) > 1000 else (yt.description or "No description available"),
            "length": yt.length,
            "views": yt.views,
            "author": yt.author,
            "publish_date": str(yt.publish_date) if yt.publish_date else "Unknown",
            "source": "pytube"
        }
    except Exception as e:
        logger.warning(f"Pytube failed: {str(e)}")
    
    # Method 2: Try YouTube Data API
    api_info = get_video_info_from_api(video_id)
    if api_info:
        return api_info
    
    # Method 3: Try webpage extraction
    webpage_info = get_video_info_from_webpage(url)
    if webpage_info:
        return webpage_info
    
    # Method 4: Final fallback with better error message
    return {
        "title": f"YouTube Video (ID: {video_id})",
        "description": "Unable to retrieve video details due to YouTube API restrictions. This appears to be a valid YouTube video, but detailed metadata is not accessible at this time.",
        "length": "Unknown",
        "views": "Unknown", 
        "author": "Unknown",
        "publish_date": "Unknown",
        "source": "fallback"
    }

def get_video_transcript(url):
    """Extract transcript/captions from YouTube video using youtube-transcript-api"""
    try:
        logger.info(f"Attempting to extract transcript from: {url}")
        
        # Extract video ID from URL
        video_id = extract_video_id(url)
        if not video_id:
            logger.error("Could not extract video ID from URL")
            return None
        
        logger.info(f"Extracted video ID: {video_id}")
        
        # Try to get transcript using youtube-transcript-api (more reliable)
        try:
            # First try to get English transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            
            # Combine all transcript entries into one text
            transcript_parts = []
            for entry in transcript_list:
                text = entry['text']
                
                # Clean up the text
                text = text.strip()
                # Remove common caption artifacts
                text = re.sub(r'\[.*?\]', '', text)  # Remove [Music], [Applause], etc.
                text = re.sub(r'\(.*?\)', '', text)  # Remove (inaudible), etc.
                text = re.sub(r'&amp;', '&', text)  # Fix HTML entities
                text = re.sub(r'&lt;', '<', text)
                text = re.sub(r'&gt;', '>', text)
                
                if text.strip():
                    transcript_parts.append(text.strip())
            
            full_transcript = ' '.join(transcript_parts)
            
            if full_transcript.strip():
                logger.info(f"Successfully extracted transcript: {len(full_transcript)} characters")
                return full_transcript
            
        except Exception as e:
            logger.warning(f"Primary transcript extraction failed: {str(e)}")
            
            # Fallback: Try to get any available transcript
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                for transcript in transcript_list:
                    try:
                        logger.info(f"Trying transcript language: {transcript.language}")
                        
                        # Get the transcript data
                        transcript_data = transcript.fetch()
                        
                        # Combine all transcript entries
                        transcript_parts = []
                        for entry in transcript_data:
                            text = entry['text']
                            
                            # Clean up the text
                            text = text.strip()
                            text = re.sub(r'\[.*?\]', '', text)
                            text = re.sub(r'\(.*?\)', '', text)
                            text = re.sub(r'&amp;', '&', text)
                            text = re.sub(r'&lt;', '<', text)
                            text = re.sub(r'&gt;', '>', text)
                            
                            if text.strip():
                                transcript_parts.append(text.strip())
                        
                        full_transcript = ' '.join(transcript_parts)
                        
                        if full_transcript.strip():
                            logger.info(f"Successfully extracted transcript in {transcript.language}: {len(full_transcript)} characters")
                            return full_transcript
                        
                    except Exception as inner_e:
                        logger.warning(f"Failed to get transcript in {transcript.language}: {str(inner_e)}")
                        continue
                        
            except Exception as list_error:
                logger.warning(f"Could not list available transcripts: {str(list_error)}")
        
        # Final fallback: Try pytube as backup
        logger.info("Attempting pytube fallback for transcript extraction...")
        try:
            yt = YouTube(url)
            
            # Try to get English captions first
            caption_languages = ['en', 'en-US', 'en-GB', 'a.en']
            
            for lang in caption_languages:
                try:
                    caption = yt.captions.get_by_language_code(lang)
                    if caption:
                        logger.info(f"Found pytube captions in language: {lang}")
                        
                        # Get the caption content
                        caption_xml = caption.xml_captions
                        
                        # Parse XML and extract text
                        import xml.etree.ElementTree as ET
                        root = ET.fromstring(caption_xml)
                        transcript_parts = []
                        
                        for text_element in root.findall('.//text'):
                            text_content = text_element.text
                            if text_content:
                                # Clean up the text
                                text_content = text_content.strip()
                                text_content = re.sub(r'\[.*?\]', '', text_content)
                                text_content = re.sub(r'\(.*?\)', '', text_content)
                                text_content = re.sub(r'&amp;', '&', text_content)
                                text_content = re.sub(r'&lt;', '<', text_content)
                                text_content = re.sub(r'&gt;', '>', text_content)
                                
                                if text_content.strip():
                                    transcript_parts.append(text_content.strip())
                        
                        full_transcript = ' '.join(transcript_parts)
                        
                        if full_transcript.strip():
                            logger.info(f"Successfully extracted pytube transcript: {len(full_transcript)} characters")
                            return full_transcript
                            
                except Exception as e:
                    logger.warning(f"Failed to get pytube captions for language {lang}: {str(e)}")
                    continue
                    
        except Exception as pytube_error:
            logger.warning(f"Pytube fallback failed: {str(pytube_error)}")
        
        # If no transcript found anywhere
        logger.warning("No transcript found with any method")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting transcript: {str(e)}")
        return None

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
        combined_summaries = "\n\n".join([f"Section {i+1}: {summary}" for i, summary in enumerate(chunk_summaries)])
        
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
    """Generate natural, user-friendly summary using Gemini AI with real transcript"""
    try:
        # First, try to get the actual transcript
        transcript = None
        if url:
            logger.info("Attempting to extract video transcript...")
            transcript = get_video_transcript(url)
        
        if action == "summarize":
            if transcript:
                logger.info(f"Using transcript for summarization ({len(transcript)} characters)")
                
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
"""
                    
                    response = model.generate_content(prompt)
                    return response.text
                
                else:
                    # Long video, use chunking approach
                    logger.info(f"Long video detected, processing {len(chunks)} chunks")
                    
                    chunk_summaries = []
                    for i, chunk in enumerate(chunks):
                        logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                        chunk_summary = summarize_chunk(chunk, video_info, i+1, len(chunks))
                        chunk_summaries.append(chunk_summary)
                        
                        # Add a small delay to avoid rate limiting
                        time.sleep(0.5)
                    
                    # Create final cohesive summary
                    final_summary = create_final_summary(chunk_summaries, video_info)
                    return final_summary
            
            else:
                # Fallback to metadata-based summary
                logger.warning("No transcript available, falling back to metadata-based summary")
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
                else:
                    # Very minimal data - provide a helpful response
                    video_id = extract_video_id(url) if url else "unknown"
                    return f"""I don't have access to detailed information about this YouTube video (ID: {video_id}) due to current API restrictions. 

Instead of giving you a generic response, let me be honest: I can't provide a meaningful summary without being able to access the video's title, description, or transcript. 

Here's what I recommend:
1. Try watching the first 30 seconds to see if it interests you
2. Check the video's comments for insights from other viewers  
3. Look at the channel's other videos to understand their content style
4. Use the video's chapters/timestamps if available

I apologize that I can't give you the detailed summary you're looking for. YouTube's API restrictions are preventing me from accessing the content needed to provide a useful analysis."""
                
        else:  # transcribe
            if transcript:
                # For transcribe action, return the cleaned transcript with some context
                duration_text = f"{video_info['length']} seconds" if video_info['length'] != "Unknown" else "Unknown duration"
                
                prompt = f"""
You have the transcript of a YouTube video. Present it in a natural, readable format with some context.

Video: "{video_info['title']}" by {video_info['author']} ({duration_text})

Transcript:
{transcript}

Clean up this transcript and present it in a readable format. Add paragraph breaks where appropriate, 
fix obvious transcription errors, and make it flow naturally. Keep all the content but make it easier to read.
"""
                
                response = model.generate_content(prompt)
                return response.text
            else:
                # Fallback for transcribe when no transcript available
                logger.warning("No transcript available for transcription request")
                return "Transcript not available for this video. This could be because the video doesn't have captions, or the captions are not in English. You can try using the 'summarize' option instead, which works with video metadata."

    except Exception as e:
        logger.error(f"Error generating content with Gemini: {str(e)}")
        return f"❌ Error generating AI analysis: {str(e)}\n\nPlease check your Gemini API key and internet connection."

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Gemini AI Server is running",
        timestamp=time.time()
    )

@app.post("/process-video", response_model=ProcessResponse)
async def process_video(request: VideoProcessRequest):
    """Process video for transcription or summarization using Gemini AI"""
    
    start_time = time.time()
    
    try:
        logger.info(f"Processing video: {request.videoId}, action: {request.action}")
        
        # Validate request
        if request.action not in ['transcribe', 'summarize']:
            raise HTTPException(status_code=400, detail="Invalid action. Must be 'transcribe' or 'summarize'")
        
        # Extract video ID and validate URL
        video_id = extract_video_id(request.url)
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        # Get video information
        video_info = get_video_info(request.url)
        
        # Generate AI content using Gemini with transcript extraction
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
                    "views": video_info['views']
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
                    "publish_date": video_info['publish_date']
                }
            }
        
        processing_time = time.time() - start_time
        
        logger.info(f"Successfully processed video {video_id} in {processing_time:.2f} seconds")
        
        return ProcessResponse(
            success=True,
            data=result_data,
            error=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
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

@app.post("/quick-summary")
async def quick_summary():
    """Quick summary endpoint that returns just the summary text"""
    try:
        response = model.generate_content("Tell me about how AI is transforming the world today in a natural, conversational way. Keep it engaging and friendly, like you're explaining it to a curious friend.")
        return {
            "summary": response.text
        }
    except Exception as e:
        return {
            "error": str(e)
        }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "YouTube Video Summarizer API - Gemini AI Powered",
        "status": "running",
        "ai_model": "Google Gemini 1.5 Flash",
        "docs": "/docs",
        "health": "/health",
        "version": "2.0.0-gemini"
    }

if __name__ == "__main__":
    try:
        import uvicorn
        
        logger.info("🤖 Starting YouTube Video Summarizer Backend with Gemini AI")
        logger.info("🌐 Server will be available at: http://localhost:8002")
        logger.info("📚 API documentation at: http://localhost:8002/docs")
        logger.info("🧠 Powered by Google Gemini 1.5 Flash")
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
