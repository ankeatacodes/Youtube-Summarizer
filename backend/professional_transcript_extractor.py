"""
Professional Multi-layered Transcript Extraction System
Mirrors how professional tools like Sider/Eightify handle YouTube videos
with proper fallback hierarchy and graceful degradation
"""

import re
import time
import logging
import requests
from typing import Optional, Dict, List
import json
import html
import subprocess
import tempfile
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfessionalTranscriptExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        })

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
            r'youtu\.be\/([0-9A-Za-z_-]{11})',
            r'shorts\/([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_transcript_professional(self, url: str) -> Dict:
        """
        Professional multi-layered transcript extraction
        Returns: {
            'transcript': str or None,
            'method': str,
            'success': bool,
            'error': str or None
        }
        """
        video_id = self.extract_video_id(url)
        if not video_id:
            return {
                'transcript': None,
                'method': 'none',
                'success': False,
                'error': 'Invalid YouTube URL - could not extract video ID'
            }

        logger.info(f"🎯 Starting professional transcript extraction for: {video_id}")

        # Layer 1: Primary - youtube-transcript-api (most reliable for actual subtitles)
        result = self._try_youtube_transcript_api(video_id)
        if result['success']:
            return result

        # Layer 2: Secondary - yt-dlp (for auto-generated captions)
        result = self._try_ytdlp_extraction(video_id, url)
        if result['success']:
            return result

        # Layer 3: Tertiary - Web scraping fallback
        result = self._try_web_scraping_captions(video_id, url)
        if result['success']:
            return result

        # Layer 4: Last resort - return graceful failure
        return {
            'transcript': None,
            'method': 'all_failed',
            'success': False,
            'error': 'All transcript extraction methods failed. Video may not have captions or may be region-restricted.'
        }

    def _try_youtube_transcript_api(self, video_id: str) -> Dict:
        """Layer 1: Try youtube-transcript-api (most reliable)"""
        try:
            logger.info("📋 Trying YouTube Transcript API (Layer 1)...")
            
            # Import here to handle missing dependency gracefully
            try:
                from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
            except ImportError:
                logger.debug("youtube-transcript-api not available")
                return {
                    'transcript': None,
                    'method': 'youtube_transcript_api',
                    'success': False,
                    'error': 'youtube-transcript-api not installed'
                }
            
            # Try to get English transcript first
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                transcript_text = " ".join([entry['text'] for entry in transcript_list])
                
                if transcript_text and len(transcript_text.strip()) > 50:
                    cleaned_transcript = self._clean_transcript_text(transcript_text)
                    logger.info(f"✅ Success with YouTube Transcript API: {len(cleaned_transcript)} characters")
                    return {
                        'transcript': cleaned_transcript,
                        'method': 'youtube_transcript_api',
                        'success': True,
                        'error': None
                    }
                    
            except (TranscriptsDisabled, NoTranscriptFound):
                logger.debug("No English transcript found, trying other languages...")
                
                # Try other language variants
                language_codes = ['en-US', 'en-GB', 'en-CA', 'en-AU', 'a.en']
                for lang in language_codes:
                    try:
                        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                        transcript_text = " ".join([entry['text'] for entry in transcript_list])
                        
                        if transcript_text and len(transcript_text.strip()) > 50:
                            cleaned_transcript = self._clean_transcript_text(transcript_text)
                            logger.info(f"✅ Success with YouTube Transcript API ({lang}): {len(cleaned_transcript)} characters")
                            return {
                                'transcript': cleaned_transcript,
                                'method': f'youtube_transcript_api_{lang}',
                                'success': True,
                                'error': None
                            }
                    except Exception:
                        continue

            except VideoUnavailable:
                logger.warning("Video is unavailable")
                return {
                    'transcript': None,
                    'method': 'youtube_transcript_api',
                    'success': False,
                    'error': 'Video is unavailable or private'
                }

            except Exception as e:
                logger.debug(f"YouTube Transcript API error: {e}")

        except Exception as e:
            logger.debug(f"YouTube Transcript API failed: {e}")

        return {
            'transcript': None,
            'method': 'youtube_transcript_api',
            'success': False,
            'error': 'No transcript available via YouTube Transcript API'
        }

    def _try_ytdlp_extraction(self, video_id: str, url: str) -> Dict:
        """Layer 2: Try yt-dlp for auto-generated captions"""
        try:
            logger.info("🔧 Trying yt-dlp extraction (Layer 2)...")
            
            # Check if yt-dlp is available
            try:
                subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True, timeout=5)
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                logger.debug("yt-dlp not available, skipping...")
                return {
                    'transcript': None,
                    'method': 'ytdlp',
                    'success': False,
                    'error': 'yt-dlp not installed or not accessible'
                }

            # Try to extract subtitle information
            try:
                cmd = [
                    'yt-dlp', 
                    '--write-auto-subs', 
                    '--skip-download', 
                    '--sub-lang', 'en',
                    '--dump-json',
                    url
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and result.stdout:
                    try:
                        info = json.loads(result.stdout)
                        automatic_captions = info.get("automatic_captions", {})
                        
                        # Look for English automatic captions
                        if 'en' in automatic_captions and automatic_captions['en']:
                            subtitle_url = automatic_captions['en'][0].get('url')
                            if subtitle_url:
                                # Download and parse the subtitle file
                                subtitle_text = self._download_and_parse_subtitles(subtitle_url)
                                if subtitle_text:
                                    cleaned_transcript = self._clean_transcript_text(subtitle_text)
                                    logger.info(f"✅ Success with yt-dlp: {len(cleaned_transcript)} characters")
                                    return {
                                        'transcript': cleaned_transcript,
                                        'method': 'ytdlp_auto_captions',
                                        'success': True,
                                        'error': None
                                    }
                    except json.JSONDecodeError:
                        logger.debug("Could not parse yt-dlp JSON output")
                        
            except subprocess.TimeoutExpired:
                logger.debug("yt-dlp timed out")
            except Exception as e:
                logger.debug(f"yt-dlp execution error: {e}")

        except Exception as e:
            logger.debug(f"yt-dlp method failed: {e}")

        return {
            'transcript': None,
            'method': 'ytdlp',
            'success': False,
            'error': 'yt-dlp extraction failed or no auto-captions available'
        }

    def _try_web_scraping_captions(self, video_id: str, url: str) -> Dict:
        """Layer 3: Try web scraping for caption data (minimal implementation)"""
        logger.info("🌐 Trying web scraping fallback (Layer 3)...")
        
        # This layer is intentionally minimal as web scraping is very unreliable
        # Professional tools typically don't rely heavily on this method
        return {
            'transcript': None,
            'method': 'web_scraping',
            'success': False,
            'error': 'Web scraping method not implemented (too unreliable for production use)'
        }

    def _download_and_parse_subtitles(self, subtitle_url: str) -> Optional[str]:
        """Download and parse subtitle file from URL"""
        try:
            response = self.session.get(subtitle_url, timeout=10)
            if response.status_code == 200:
                # Parse subtitle content (usually WebVTT or SRT format)
                content = response.text
                
                # Remove WebVTT headers and timing info
                lines = content.split('\\n')
                text_lines = []
                
                for line in lines:
                    line = line.strip()
                    # Skip empty lines, timestamps, and WebVTT headers
                    if (line and 
                        not line.startswith('WEBVTT') and
                        not line.startswith('NOTE') and
                        not '-->' in line and
                        not re.match(r'^\\d+$', line) and
                        not re.match(r'^\\d{2}:\\d{2}:\\d{2}', line)):
                        text_lines.append(line)
                
                if text_lines:
                    return ' '.join(text_lines)
                    
        except Exception as e:
            logger.debug(f"Subtitle download failed: {e}")
        
        return None

    def get_video_info_robust(self, url: str) -> Dict:
        """
        Professional video info extraction with proper fallback
        Always returns something useful, never crashes
        """
        video_id = self.extract_video_id(url)
        if not video_id:
            return self._create_fallback_info(None, "Invalid URL")

        logger.info(f"📊 Extracting video info for: {video_id}")

        # Try pytube first (when it works, it's most comprehensive)
        try:
            logger.info("📺 Trying pytube for video info...")
            
            # Import here to handle missing dependency gracefully
            try:
                from pytube import YouTube
            except ImportError:
                logger.debug("pytube not available")
                raise ImportError("pytube not installed")
            
            yt = YouTube(url)
            info = {
                "title": yt.title or f"YouTube Video (ID: {video_id})",
                "description": self._truncate_description(yt.description),
                "length": yt.length,
                "views": yt.views,
                "author": yt.author or "Unknown",
                "publish_date": str(yt.publish_date) if yt.publish_date else "Unknown",
                "video_id": video_id,
                "source": "pytube"
            }
            
            logger.info(f"✅ pytube success: {info['title']}")
            return info
            
        except Exception as e:
            logger.debug(f"pytube failed: {e}")

        # Fallback to web scraping with improved reliability
        try:
            logger.info("🌐 Trying improved web scraping for video info...")
            clean_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Use more browser-like headers (without compression to avoid decoding issues)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            response = requests.get(clean_url, headers=headers, timeout=20)
            if response.status_code != 200:
                logger.debug(f"HTTP {response.status_code} when fetching video page")
                return self._create_fallback_info(video_id, f"HTTP {response.status_code}")

            content = response.text
            logger.debug(f"Web scraping got content length: {len(content)}")
            
            info = self._extract_info_from_page(content, video_id)
            logger.debug(f"Extracted info: {info}")
            
            # Even if we only got the title, that's better than nothing
            if info.get('title') and not info['title'].startswith("YouTube Video (ID:"):
                logger.info(f"✅ Web scraping success: {info['title']}")
                return info
            else:
                logger.debug("Web scraping didn't extract meaningful title")
                
        except Exception as e:
            logger.debug(f"Web scraping failed: {e}")
            import traceback
            logger.debug(f"Full traceback: {traceback.format_exc()}")

        # Final fallback
        return self._create_fallback_info(video_id, "All extraction methods failed")

    def _extract_info_from_page(self, content: str, video_id: str) -> Dict:
        """Extract video info from YouTube page HTML"""
        info = {
            'video_id': video_id,
            'source': 'web_scraping'
        }

        # Extract title (multiple methods with better patterns)
        title = None
        
        try:
            # Method 1: Page title (improved pattern)
            title_patterns = [
                r'<title>([^<]+)</title>',
                r'<title[^>]*>([^<]+)</title>',
                r'"title":"([^"]+)"',
                r'property="og:title" content="([^"]+)"',
                r'name="title" content="([^"]+)"',            # This was missing!
            ]
            
            # Debug: show content sample
            sample = content[:3000] if len(content) > 3000 else content
            logger.debug(f"Content sample (first 3000 chars): {sample}")
            
            for i, pattern in enumerate(title_patterns):
                logger.debug(f"Testing pattern {i+1}: '{pattern}'")
                title_match = re.search(pattern, content, re.IGNORECASE)
                if title_match:
                    raw_title = title_match.group(1)
                    processed_title = raw_title.replace(' - YouTube', '').strip()
                    logger.debug(f"Pattern matched: '{pattern}' -> Raw: '{raw_title}' -> Processed: '{processed_title}'")
                    
                    if processed_title and processed_title != 'YouTube' and not processed_title.startswith('YouTube'):
                        title = html.unescape(processed_title)
                        logger.debug(f"Extracted title: '{title}'")
                        break
                    else:
                        logger.debug(f"Title rejected: '{processed_title}' (empty={not processed_title}, is_youtube={processed_title == 'YouTube'}, starts_with_youtube={processed_title.startswith('YouTube') if processed_title else False})")
                else:
                    logger.debug(f"Pattern failed: '{pattern}'")
            
            # Method 2: JSON-LD
            if not title:
                json_ld_pattern = r'<script type="application/ld\\+json"[^>]*>(.*?)</script>'
                matches = re.findall(json_ld_pattern, content, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match)
                        if isinstance(data, dict) and data.get('@type') == 'VideoObject':
                            title = data.get('name')
                            if title:
                                logger.debug(f"Extracted title from JSON-LD: '{title}'")
                                break
                    except:
                        continue

            # Method 3: ytInitialData
            if not title:
                try:
                    pattern = r'var ytInitialData = ({.*?});'
                    match = re.search(pattern, content)
                    if match:
                        data = json.loads(match.group(1))
                        title = self._extract_title_from_initial_data(data)
                        if title:
                            logger.debug(f"Extracted title from ytInitialData: '{title}'")
                except:
                    pass

            info['title'] = title or f"YouTube Video (ID: {video_id})"
            logger.debug(f"Final title set: '{info['title']}'")
            
            # Extract other metadata
            info.update({
                'description': self._extract_description(content),
                'author': self._extract_author(content),
                'length': 'Unknown',
                'views': 'Unknown',
                'publish_date': 'Unknown'
            })

            logger.debug(f"Final extracted info: {info}")
            return info
            
        except Exception as e:
            logger.error(f"Error in _extract_info_from_page: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                'video_id': video_id,
                'source': 'web_scraping_error',
                'title': f"YouTube Video (ID: {video_id})",
                'description': 'Error extracting info',
                'author': 'Unknown',
                'length': 'Unknown',
                'views': 'Unknown',
                'publish_date': 'Unknown'
            }

    def _extract_title_from_initial_data(self, data: Dict) -> Optional[str]:
        """Extract title from ytInitialData"""
        try:
            # Navigate the complex YouTube data structure
            if 'videoDetails' in data:
                return data['videoDetails'].get('title')
            
            # Try different paths in the data structure
            contents = data.get('contents', {})
            if isinstance(contents, dict):
                # This would need more specific navigation
                # For now, return None to avoid errors
                pass
        except:
            pass
        return None

    def _extract_description(self, content: str) -> str:
        """Extract description from page with multiple methods"""
        patterns = [
            r'<meta property="og:description" content="([^"]+)"',
            r'<meta name="description" content="([^"]+)"',
            r'"description":{"simpleText":"([^"]+)"',
            r'"shortDescription":"([^"]+)"'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                desc = html.unescape(match.group(1))
                if desc and len(desc.strip()) > 10:  # Ensure meaningful description
                    return self._truncate_description(desc)
        
        return "No description available"

    def _extract_author(self, content: str) -> str:
        """Extract author/channel name from page with multiple methods"""
        patterns = [
            r'"author":"([^"]+)"',
            r'<meta name="author" content="([^"]+)"',
            r'"channelName":"([^"]+)"',
            r'"ownerChannelName":"([^"]+)"',
            r'property="og:video:tag" content="([^"]+)"'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                author = html.unescape(match.group(1))
                if author and len(author.strip()) > 1 and author != "YouTube":
                    return author
        
        return "Unknown"

    def _truncate_description(self, description: Optional[str]) -> str:
        """Truncate description to reasonable length"""
        if not description:
            return "No description available"
        
        if len(description) > 1000:
            return description[:1000] + "..."
        return description

    def _create_fallback_info(self, video_id: Optional[str], reason: str) -> Dict:
        """Create fallback video info when extraction fails"""
        return {
            'title': f"YouTube Video (ID: {video_id or 'unknown'})",
            'description': f"Unable to retrieve video details. Reason: {reason}",
            'length': 'Unknown',
            'views': 'Unknown',
            'author': 'Unknown',
            'publish_date': 'Unknown',
            'video_id': video_id,
            'source': 'fallback'
        }

    def _clean_transcript_text(self, text: str) -> str:
        """Clean and normalize transcript text"""
        if not text:
            return ""
        
        # Remove common transcript artifacts
        text = re.sub(r'\\[.*?\\]', '', text)  # Remove [Music], [Applause], etc.
        text = re.sub(r'\\(.*?\\)', '', text)  # Remove (inaudible), etc.
        text = re.sub(r'&amp;', '&', text)  # Fix HTML entities
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        text = re.sub(r'&quot;', '"', text)
        text = re.sub(r'&#39;', "'", text)
        
        # Remove extra whitespace
        text = re.sub(r'\\s+', ' ', text)
        text = text.strip()
        
        # Decode HTML entities
        text = html.unescape(text)
        
        return text

# Global instance
transcript_extractor = ProfessionalTranscriptExtractor()

# Convenience functions for backward compatibility
def extract_video_id(url: str) -> Optional[str]:
    return transcript_extractor.extract_video_id(url)

def get_video_info(url: str) -> Dict:
    return transcript_extractor.get_video_info_robust(url)

def get_transcript_robust(url: str) -> Optional[str]:
    result = transcript_extractor.get_transcript_professional(url)
    return result.get('transcript') if result.get('success') else None
