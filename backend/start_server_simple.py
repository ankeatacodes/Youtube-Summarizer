import uvicorn
import sys
sys.path.append('.')
from professional_gemini_server import app

print('Starting server on port 8002...')
uvicorn.run(app, host='0.0.0.0', port=8002, log_level='info')
