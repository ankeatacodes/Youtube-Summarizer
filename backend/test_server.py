"""
Simple test version of the YouTube Summarizer API backend
This version tests basic functionality without heavy AI dependencies
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse as urlparse
from urllib.parse import parse_qs
import time
import os

class TestAPIHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        """Handle preflight requests"""
        self._set_headers()

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse.urlparse(self.path)
        
        if parsed_path.path == '/health':
            self._set_headers()
            response = {
                "status": "healthy",
                "message": "YouTube Summarizer Test API is running",
                "timestamp": time.time()
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif parsed_path.path == '/models/status':
            self._set_headers()
            response = {
                "whisper": False,
                "llama": False,
                "prompt_node": False,
                "pipeline": False,
                "model_path_exists": False,
                "message": "Test mode - AI models not loaded"
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif parsed_path.path == '/':
            self._set_headers()
            response = {
                "message": "YouTube Video Summarizer Test API",
                "version": "1.0.0-test",
                "docs": "/docs (not available in test mode)",
                "health": "/health"
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self._set_headers(404)
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/process-video':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode())
                
                # Simulate processing
                video_url = request_data.get('url', '')
                action = request_data.get('action', 'transcribe')
                video_id = request_data.get('videoId', 'unknown')
                
                print(f"Processing request: {action} for {video_url}")
                
                # Simulate processing time
                time.sleep(2)
                
                # Create mock response
                if action == 'summarize':
                    result = {
                        "transcription": f"[TEST MODE] This is a mock transcription of the video: {video_url}. The video discusses various topics and provides valuable information to viewers.",
                        "summary": f"[TEST MODE] Summary: This video covers important topics and provides insights. Key points include educational content and practical examples.",
                        "video_id": video_id,
                        "action": action
                    }
                else:
                    result = {
                        "transcription": f"[TEST MODE] This is a mock transcription of the video: {video_url}. The video discusses various topics and provides valuable information to viewers.",
                        "video_id": video_id,
                        "action": action
                    }
                
                self._set_headers()
                response = {
                    "success": True,
                    "data": result,
                    "processing_time": 2.0
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                print(f"Error processing request: {e}")
                self._set_headers(500)
                response = {
                    "success": False,
                    "error": f"Internal server error: {str(e)}"
                }
                self.wfile.write(json.dumps(response).encode())
        else:
            self._set_headers(404)
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        """Override to add custom logging"""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def run_test_server(port=8000):
    """Run the test server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, TestAPIHandler)
    
    print(f"🎥 YouTube Summarizer Test API Server")
    print(f"🌐 Server running on http://localhost:{port}")
    print(f"📚 Health check: http://localhost:{port}/health")
    print(f"🧪 Test mode - Mock responses will be returned")
    print(f"🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()

if __name__ == "__main__":
    run_test_server()
