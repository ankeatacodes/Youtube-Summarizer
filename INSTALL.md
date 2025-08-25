# Chrome Extension Installation Instructions

## Quick Install Guide

### 1. Prepare the Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

The server should start at http://localhost:8000

### 2. Install Chrome Extension

1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable "Developer mode" (top-right toggle)
4. Click "Load unpacked"
5. Select the `chrome-extension` folder
6. Pin the extension to your toolbar

### 3. Test the Extension

1. Go to any YouTube video
2. Click the extension icon or the floating "Summarize" button
3. Click "Summarize Video" or "Transcribe Only"

## Troubleshooting

**Backend not connecting?**
- Make sure the server is running on http://localhost:8000
- Check the settings in the extension popup

**Extension not showing?**
- Refresh the YouTube page
- Check if the extension is enabled in chrome://extensions/

**Model errors?**
- The extension works without the Llama 2 model (transcription only)
- Download the model file for full summarization features

## Features

✅ Real-time video transcription  
✅ AI-powered summarization  
✅ Floating action button on YouTube  
✅ Settings and preferences  
✅ Local storage of results  
✅ Background processing  

Enjoy your new YouTube video summarizer! 🎥✨
