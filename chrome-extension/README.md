# YouTube Video Summarizer - Chrome Extension

A full-stack Chrome extension that provides AI-powered transcription and summarization of YouTube videos using Llama 2, Whisper, and Haystack.

## 🚀 Features

- **Real-time transcription** using OpenAI Whisper
- **AI-powered summarization** using Llama 2 (32K context)
- **Chrome extension interface** with floating action button
- **Background processing** via FastAPI backend
- **Local storage** for summaries and settings
- **Settings panel** for customization

## 📁 Project Structure

```
├── chrome-extension/          # Chrome extension files
│   ├── manifest.json         # Extension manifest
│   ├── popup.html/js         # Extension popup interface
│   ├── content.js            # YouTube page interaction
│   ├── background.js         # Background service worker
│   ├── settings.html/js      # Settings page
│   └── icons/               # Extension icons
├── backend/                  # FastAPI backend server
│   ├── main.py              # Main API server
│   ├── model_add.py         # Llama 2 integration
│   ├── requirements.txt     # Python dependencies
│   ├── start.sh/.bat        # Startup scripts
│   └── downloads/           # Temporary audio files
└── README.md                # This file
```

## 🛠️ Installation & Setup

### Step 1: Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the Llama 2 model (optional):**
   - Download `llama-2-7b-32k-instruct.Q4_K_S.gguf` from [HuggingFace](https://huggingface.co/togethercomputer/LLaMA-2-7B-32K-Instruct-GGUF)
   - Place it in the `backend/` directory
   - Note: The extension works without this model (transcription only)

4. **Start the backend server:**
   
   **Windows:**
   ```bash
   start.bat
   ```
   
   **Linux/Mac:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```
   
   **Manual start:**
   ```bash
   python main.py
   ```

5. **Verify the backend is running:**
   - Open http://localhost:8000/health
   - You should see: `{"status":"healthy","message":"YouTube Summarizer API is running",...}`

### Step 2: Chrome Extension Installation

1. **Open Chrome and navigate to:**
   ```
   chrome://extensions/
   ```

2. **Enable Developer Mode** (toggle in top-right)

3. **Click "Load unpacked"**

4. **Select the `chrome-extension` folder** from this project

5. **Pin the extension** (click the puzzle piece icon in Chrome toolbar and pin "YouTube Video Summarizer")

### Step 3: Usage

1. **Navigate to any YouTube video**

2. **Click the floating "Summarize" button** that appears on the page, OR

3. **Click the extension icon** in the Chrome toolbar

4. **Choose your action:**
   - **Summarize Video**: Get AI-powered summary
   - **Transcribe Only**: Get full transcription
   - **Settings**: Configure the extension

## ⚙️ Configuration

### Extension Settings

Access via the extension popup → Settings:

- **Backend URL**: Configure the API server address (default: http://localhost:8000)
- **Auto-summarize**: Automatically process videos when visiting YouTube
- **Summary Length**: Choose detail level (short/medium/long)
- **Notifications**: Enable/disable completion notifications

### Backend Configuration

Edit `.env` file in the backend directory:

```env
# Copy from .env.example and modify as needed
MODEL_PATH=llama-2-7b-32k-instruct.Q4_K_S.gguf
USE_GPU=false
MAX_TOKENS=512
TEMPERATURE=0.1
```

## 🔧 API Endpoints

The backend provides these endpoints:

- `GET /health` - Health check
- `POST /process-video` - Process YouTube video
- `GET /models/status` - Check model availability
- `GET /docs` - Interactive API documentation

## 🐛 Troubleshooting

### Backend Issues

1. **"Backend is not running" error:**
   - Ensure the backend server is started (`python main.py`)
   - Check if port 8000 is available
   - Verify no firewall is blocking the connection

2. **Model loading errors:**
   - Ensure the model file exists in the backend directory
   - Check available RAM (model requires ~4GB)
   - Try without GPU if CUDA issues occur

3. **YouTube download failures:**
   - Some videos may be restricted
   - Check internet connection
   - Verify `pytube` is working: `python -c "from pytube import YouTube; print('OK')"`

### Extension Issues

1. **Extension not appearing:**
   - Refresh the YouTube page
   - Check if extension is enabled in chrome://extensions/
   - Look for error messages in Chrome DevTools console

2. **"No video data" error:**
   - Ensure you're on a YouTube video page (`/watch?v=...`)
   - Refresh the page and try again
   - Check browser console for errors

3. **Settings not saving:**
   - Check Chrome extension storage permissions
   - Try refreshing the extension (disable/enable)

## 📊 Performance Notes

- **First run** may take longer (model loading)
- **Video length** affects processing time
- **Model size** impacts summarization quality vs. speed
- **GPU acceleration** significantly improves performance

## 🔐 Privacy & Security

- **Local processing**: All data stays on your machine
- **No tracking**: Extension doesn't collect user data
- **Temporary files**: Audio files are automatically cleaned up
- **CORS protection**: Backend includes security headers

## 🆕 Migration from Original Streamlit App

This Chrome extension replaces the original Streamlit interface with:

1. **Better UX**: Direct integration with YouTube
2. **Background processing**: Non-blocking video analysis
3. **Persistent storage**: Saves summaries for later viewing
4. **Cross-platform**: Works on any system with Chrome
5. **API architecture**: Separates frontend and backend concerns

## 📝 Development

### Adding New Features

1. **Frontend**: Modify files in `chrome-extension/`
2. **Backend**: Update `backend/main.py` and related files
3. **Models**: Extend `backend/model_add.py` for new AI models

### Testing

1. **Backend**: Use the FastAPI docs at http://localhost:8000/docs
2. **Extension**: Use Chrome DevTools for debugging
3. **Integration**: Test with various YouTube videos

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 🙏 Acknowledgments

- **Llama 2** by Meta AI
- **Whisper** by OpenAI
- **Haystack** by deepset
- **FastAPI** by Sebastián Ramirez
- **pytube** for YouTube integration

---

**Built with ❤️ for the developer community**
