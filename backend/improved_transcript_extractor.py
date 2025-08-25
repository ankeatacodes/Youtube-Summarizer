"""
Multi-layered Transcript Extraction (Professional Approach)
Mirrors how tools like Sider/Eightify handle YouTube transcript extraction
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
from urllib.parse import parse_qs, urlparse
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

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
        """Layer 3: Try web scraping for caption data"""
        try:
            logger.info("🌐 Trying web scraping fallback (Layer 3)...")
            
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return {
                    'transcript': None,
                    'method': 'web_scraping',
                    'success': False,
                    'error': f'HTTP {response.status_code} when accessing video page'
                }

            content = response.text
            
            # Look for player response data that might contain caption info
            patterns = [
                r'"captions":\s*({[^}]*"playerCaptionsTracklistRenderer"[^}]*})',
                r'"playerCaptionsTracklistRenderer":\s*({.*?})',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    logger.debug("Found potential caption data in page")
                    # This would need more complex parsing
                    # For now, we'll skip this as it's very brittle
                    break

            # Alternative: Look for transcript in page source (some videos have this)
            transcript_patterns = [
                r'"transcriptRenderer".*?"cueGroups":\s*\[(.*?)\]',
                r'"transcript":\s*"([^"]*)"',
            ]
            
            for pattern in transcript_patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    logger.debug("Found potential transcript in page source")
                    # This would need careful parsing
                    break

        except Exception as e:
            logger.debug(f"Web scraping failed: {e}")

        return {
            'transcript': None,
            'method': 'web_scraping',
            'success': False,
            'error': 'Web scraping method not implemented (too unreliable)'
        }

    def _download_and_parse_subtitles(self, subtitle_url: str) -> Optional[str]:
        """Download and parse subtitle file from URL"""
        try:
            response = self.session.get(subtitle_url, timeout=10)
            if response.status_code == 200:
                # Parse subtitle content (usually WebVTT or SRT format)
                content = response.text
                
                # Remove WebVTT headers and timing info
                lines = content.split('\n')
                text_lines = []
                
                for line in lines:
                    line = line.strip()
                    # Skip empty lines, timestamps, and WebVTT headers
                    if (line and 
                        not line.startswith('WEBVTT') and
                        not line.startswith('NOTE') and
                        not '-->' in line and
                        not re.match(r'^\d+$', line) and
                        not re.match(r'^\d{2}:\d{2}:\d{2}', line)):
                        text_lines.append(line)
                
                if text_lines:
                    return ' '.join(text_lines)
                    
        except Exception as e:
            logger.debug(f"Subtitle download failed: {e}")
        
        return None

    def get_video_info_robust(self, url: str) -> Dict:
        """Get video information using web scraping with improved error handling"""
        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                return self._create_fallback_info(video_id)

            # Clean URL for request
            clean_url = f"https://www.youtube.com/watch?v={video_id}"
            
            response = self.session.get(clean_url, timeout=15)
            if response.status_code != 200:
                logger.warning(f"HTTP {response.status_code} when fetching video page")
                return self._create_fallback_info(video_id)

            content = response.text
            
            # Extract information from various sources
            info = {}
            
            # Method 1: Try to extract from JSON-LD
            json_ld_info = self._extract_from_json_ld(content)
            if json_ld_info:
                info.update(json_ld_info)
            
            # Method 2: Extract from page title
            title_info = self._extract_from_title(content)
            if title_info and 'title' not in info:
                info.update(title_info)
            
            # Method 3: Extract from meta tags
            meta_info = self._extract_from_meta_tags(content)
            if meta_info:
                info.update(meta_info)
            
            # Method 4: Extract from ytInitialData
            initial_data_info = self._extract_from_initial_data(content)
            if initial_data_info:
                info.update(initial_data_info)
            
            # Ensure we have at least basic info
            if not info.get('title'):
                info['title'] = f"YouTube Video (ID: {video_id})"
            
            info.update({
                'video_id': video_id,
                'source': 'web_scraping',
                'length': info.get('length', 'Unknown'),
                'views': info.get('views', 'Unknown'),
                'author': info.get('author', 'Unknown'),
                'publish_date': info.get('publish_date', 'Unknown'),
                'description': info.get('description', 'No description available')
            })
            
            return info
            
        except Exception as e:
            logger.error(f"Error extracting video info: {e}")
            return self._create_fallback_info(self.extract_video_id(url))

    def _extract_from_json_ld(self, content: str) -> Dict:
        """Extract info from JSON-LD structured data"""
        try:
            json_ld_pattern = r'<script type="application/ld\+json"[^>]*>(.*?)</script>'
            matches = re.findall(json_ld_pattern, content, re.DOTALL)
            
            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, dict) and data.get('@type') == 'VideoObject':
                        info = {}
                        if data.get('name'):
                            info['title'] = data['name']
                        if data.get('description'):
                            info['description'] = data['description'][:1000]
                        if data.get('author', {}).get('name'):
                            info['author'] = data['author']['name']
                        if data.get('uploadDate'):
                            info['publish_date'] = data['uploadDate']
                        if data.get('duration'):
                            # Convert PT duration to seconds
                            duration = data['duration']
                            if 'PT' in duration:
                                seconds = self._parse_duration(duration)
                                if seconds:
                                    info['length'] = seconds
                        return info
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            logger.debug(f"JSON-LD extraction failed: {e}")
        return {}

    def _extract_from_title(self, content: str) -> Dict:
        """Extract title from page title tag"""
        try:
            title_match = re.search(r'<title>([^<]+)</title>', content)
            if title_match:
                title = title_match.group(1).replace(' - YouTube', '').strip()
                if title and title != 'YouTube':
                    return {'title': html.unescape(title)}
        except Exception as e:
            logger.debug(f"Title extraction failed: {e}")
        return {}

    def _extract_from_meta_tags(self, content: str) -> Dict:
        """Extract info from meta tags"""
        try:
            info = {}
            
            # Look for meta tags
            meta_patterns = {
                'title': [r'<meta property="og:title" content="([^"]+)"', r'<meta name="title" content="([^"]+)"'],
                'description': [r'<meta property="og:description" content="([^"]+)"', r'<meta name="description" content="([^"]+)"'],
                'author': [r'<meta name="author" content="([^"]+)"'],
            }
            
            for key, patterns in meta_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        info[key] = html.unescape(match.group(1))
                        break
            
            return info
        except Exception as e:
            logger.debug(f"Meta tag extraction failed: {e}")
        return {}

    def _extract_from_initial_data(self, content: str) -> Dict:
        """Extract info from ytInitialData"""
        try:
            # Look for ytInitialData
            pattern = r'var ytInitialData = ({.*?});'
            match = re.search(pattern, content)
            if not match:
                pattern = r'ytInitialData":\s*({.*?})(?:,"ytInitialPlayerResponse"|\s*};)'
                match = re.search(pattern, content)
            
            if match:
                data = json.loads(match.group(1))
                return self._parse_initial_data(data)
                
        except Exception as e:
            logger.debug(f"Initial data extraction failed: {e}")
        return {}

    def _parse_initial_data(self, data: Dict) -> Dict:
        """Parse ytInitialData for video information"""
        try:
            info = {}
            
            # Navigate through the complex YouTube data structure
            contents = data.get('contents', {})
            if 'videoDetails' in contents:
                video_details = contents['videoDetails']
            else:
                # Look in different locations
                video_details = None
                
                # Try different paths
                paths = [
                    ['contents', 'twoColumnWatchNextResults', 'results', 'results', 'contents'],
                    ['contents', 'videoDetails'],
                ]
                
                for path in paths:
                    current = data
                    for key in path:
                        if isinstance(current, dict) and key in current:
                            current = current[key]
                        else:
                            current = None
                            break
                    if current:
                        video_details = current
                        break
            
            if video_details:
                if 'title' in video_details:
                    info['title'] = video_details['title']
                if 'shortDescription' in video_details:
                    info['description'] = video_details['shortDescription'][:1000]
                if 'author' in video_details:
                    info['author'] = video_details['author']
                if 'lengthSeconds' in video_details:
                    info['length'] = int(video_details['lengthSeconds'])
                if 'viewCount' in video_details:
                    info['views'] = video_details['viewCount']
            
            return info
            
        except Exception as e:
            logger.debug(f"Initial data parsing failed: {e}")
        return {}

    def _parse_duration(self, duration: str) -> Optional[int]:
        """Parse PT duration format to seconds"""
        try:
            # PT1H30M45S -> 5445 seconds
            pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
            match = re.match(pattern, duration)
            if match:
                hours = int(match.group(1) or 0)
                minutes = int(match.group(2) or 0)
                seconds = int(match.group(3) or 0)
                return hours * 3600 + minutes * 60 + seconds
        except Exception:
            pass
        return None

    def _create_fallback_info(self, video_id: Optional[str]) -> Dict:
        """Create fallback video info when extraction fails"""
        return {
            'title': f"YouTube Video (ID: {video_id or 'unknown'})",
            'description': "Unable to retrieve video details due to access restrictions.",
            'length': 'Unknown',
            'views': 'Unknown',
            'author': 'Unknown',
            'publish_date': 'Unknown',
            'video_id': video_id,
            'source': 'fallback'
        }

    def get_transcript_robust(self, url: str) -> Optional[str]:
        """Extract transcript using multiple robust methods"""
        video_id = self.extract_video_id(url)
        if not video_id:
            logger.error("Could not extract video ID from URL")
            return None

        logger.info(f"Attempting robust transcript extraction for video ID: {video_id}")

        # Method 1: Try youtube-transcript-api with better error handling
        transcript = self._try_transcript_api(video_id)
        if transcript:
            return transcript

        # Method 2: Try direct YouTube API approach
        transcript = self._try_direct_api(video_id)
        if transcript:
            return transcript

        # Method 3: Try web scraping approach
        transcript = self._try_web_scraping(video_id)
        if transcript:
            return transcript

        logger.warning("All transcript extraction methods failed")
        return None

    def _try_transcript_api(self, video_id: str) -> Optional[str]:
        """Try youtube-transcript-api with improved error handling"""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            
            # Add delay to avoid rate limiting
            time.sleep(0.5)
            
            # Try multiple language codes
            language_codes = ['en', 'en-US', 'en-GB', 'a.en', 'en-CA', 'en-AU']
            
            for lang in language_codes:
                try:
                    logger.info(f"Trying transcript API with language: {lang}")
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                    
                    if transcript_list:
                        # Process transcript
                        text_parts = []
                        for entry in transcript_list:
                            text = entry.get('text', '').strip()
                            if text:
                                # Clean up text
                                text = self._clean_transcript_text(text)
                                if text:
                                    text_parts.append(text)
                        
                        full_transcript = ' '.join(text_parts)
                        if len(full_transcript.strip()) > 50:  # Minimum viable transcript length
                            logger.info(f"Successfully extracted transcript via API: {len(full_transcript)} characters")
                            return full_transcript
                            
                except Exception as e:
                    logger.debug(f"Failed to get transcript in {lang}: {e}")
                    continue

            # Try auto-generated as fallback
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                for transcript in transcript_list:
                    try:
                        if transcript.is_generated:
                            logger.info(f"Trying auto-generated transcript in {transcript.language}")
                            transcript_data = transcript.fetch()
                            
                            text_parts = []
                            for entry in transcript_data:
                                text = entry.get('text', '').strip()
                                if text:
                                    text = self._clean_transcript_text(text)
                                    if text:
                                        text_parts.append(text)
                            
                            full_transcript = ' '.join(text_parts)
                            if len(full_transcript.strip()) > 50:
                                logger.info(f"Successfully extracted auto-generated transcript: {len(full_transcript)} characters")
                                return full_transcript
                                
                    except Exception as e:
                        logger.debug(f"Failed to get auto-generated transcript: {e}")
                        continue
                        
            except Exception as e:
                logger.debug(f"Failed to list transcripts: {e}")

        except Exception as e:
            logger.debug(f"Transcript API completely failed: {e}")
        
        return None

    def _try_direct_api(self, video_id: str) -> Optional[str]:
        """Try direct YouTube API calls"""
        try:
            # This would require YouTube Data API v3 key
            # For now, return None as placeholder
            logger.debug("Direct API method not implemented (requires API key)")
            return None
        except Exception as e:
            logger.debug(f"Direct API failed: {e}")
        return None

    def _try_web_scraping(self, video_id: str) -> Optional[str]:
        """Try web scraping for transcript data"""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                return None
                
            content = response.text
            
            # Look for transcript data in the page
            # This is experimental and may not always work
            transcript_patterns = [
                r'"transcriptRenderer":\s*{[^}]*"cueGroups":\s*\[(.*?)\]',
                r'"captions":\s*{[^}]*"playerCaptionsTracklistRenderer"',
            ]
            
            for pattern in transcript_patterns:
                match = re.search(pattern, content)
                if match:
                    logger.debug("Found potential transcript data in page")
                    # This would need more complex parsing
                    # For now, return None
                    break
            
            return None
            
        except Exception as e:
            logger.debug(f"Web scraping failed: {e}")
        return None

    def _clean_transcript_text(self, text: str) -> str:
        """Clean and normalize transcript text"""
        if not text:
            return ""
        
        # Remove common transcript artifacts
        text = re.sub(r'\[.*?\]', '', text)  # Remove [Music], [Applause], etc.
        text = re.sub(r'\(.*?\)', '', text)  # Remove (inaudible), etc.
        text = re.sub(r'&amp;', '&', text)  # Fix HTML entities
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        text = re.sub(r'&quot;', '"', text)
        text = re.sub(r'&#39;', "'", text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Decode HTML entities
        text = html.unescape(text)
        
        return text

# Global instance
transcript_extractor = ImprovedTranscriptExtractor()
