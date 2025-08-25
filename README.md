# YouTube Video Summarizer - Full Stack Chrome Extension
AI-powered YouTube video transcription and summarization built with custom fine-tuned language model, Whisper, and Chrome Extension technology.

## 🆕 What's New - Chrome Extension Version

This project has been completely transformed from a Streamlit app into a **full-stack Chrome extension** with:

- **🔧 Chrome Extension Frontend**: Direct integration with YouTube pages
- **⚡ FastAPI Backend**: High-performance REST API server
- **🤖 AI Models**: Custom fine-tuned language model + Whisper integration
- **💾 Local Storage**: Persistent summaries and user preferences
- **🔄 Background Processing**: Non-blocking video analysis
- **⚙️ Settings Panel**: Customizable user experience

## 📝 Description:
YouTube Video Summarizer Extension is a powerful full-stack tool that automatically transcribes and summarizes YouTube videos directly in your browser. It seamlessly integrates with YouTube's interface and provides AI-powered insights without leaving the video page.

## 🚀 Quick Start

### 1. Start the Backend Server
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Server runs at: http://localhost:8000

### 2. Install Chrome Extension
1. Open Chrome → `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" → Select `chrome-extension` folder
4. Pin the extension to your toolbar

### 3. Use the Extension
1. Go to any YouTube video
2. Click the floating "Summarize" button or extension icon
3. Choose "Summarize Video" or "Transcribe Only"
4. View results in the popup or settings

## 🏗️ Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Chrome Extension  │───▶│    FastAPI Backend   │───▶│    AI Models        │
│                     │    │                      │    │                     │
│ • Popup Interface   │    │ • REST API           │    │ • Custom Fine-tuned │
│ • Content Scripts   │    │ • Video Processing   │    │ • Whisper ASR       │
│ • Background Worker │    │ • Model Integration  │    │ • Advanced Pipeline │
│ • Settings Panel    │    │ • File Management    │    │                     │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

## 💫 Core Components:

### 🔍 **Advanced AI Pipeline: Custom Fine-tuned Processing**
Proprietary AI pipeline enables efficient text processing and model integration for searching, extracting, and summarizing video content with state-of-the-art accuracy.

### 🤖 **Custom Fine-tuned Language Model: Specialized Summarization**
Personal fine-tuned language model optimized specifically for video content summarization, providing domain-specific insights and enhanced performance.

### 🗣️ **Whisper: Speech-to-Text Engine**
OpenAI's Whisper automatically transcribes spoken content from YouTube videos with high accuracy.

### 🌐 **FastAPI: High-Performance Backend**
Modern Python web framework providing async API endpoints for video processing and model inference.

### 🧩 **Chrome Extension: Seamless Integration**
Native browser extension with content scripts, background workers, and popup interface for YouTube integration.

## 📁 Project Structure

```
├── chrome-extension/          # Chrome extension files
│   ├── manifest.json         # Extension configuration
│   ├── popup.html/js         # Main interface
│   ├── content.js            # YouTube integration
│   ├── background.js         # Service worker
│   ├── settings.html/js      # Settings panel
│   └── icons/               # Extension icons
├── backend/                  # FastAPI backend
│   ├── main.py              # API server
│   ├── model_add.py         # Custom model integration
│   ├── requirements.txt     # Dependencies
│   └── start.sh/.bat        # Startup scripts
├── requirements.txt          # Original dependencies
└── yt_summary.py            # Legacy Streamlit app
```

## �️ Installation Guide

### Prerequisites
- Python 3.8+ 
- Google Chrome browser
- 4GB+ RAM (for custom fine-tuned model)

### Backend Setup
```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Custom fine-tuned model is integrated within the application
# No additional model downloads required

# Start server
python main.py
```

### Extension Installation
1. Open Chrome: `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `chrome-extension` folder
5. Pin extension to toolbar

### Docker Deployment (Alternative)
```bash
# Build and run with Docker
docker-compose up --build

# Backend available at http://localhost:8000
```

## 🎯 Usage

### Basic Usage
1. **Navigate** to any YouTube video
2. **Click** the floating "Summarize" button on the page
3. **Choose** your action:
   - **Summarize Video**: Full AI analysis
   - **Transcribe Only**: Text transcript
4. **View** results in the popup

### Advanced Features
- **Auto-summarize**: Enable in settings for automatic processing
- **Custom backend**: Configure different API endpoints
- **Summary length**: Choose detail level (short/medium/long)
- **Storage management**: View and clear saved summaries

## 🔧 Configuration

### Extension Settings
Access via popup → Settings:
- Backend URL configuration
- Auto-summarization toggle
- Summary detail preferences
- Notification settings

### Backend Configuration
Edit `.env` file:
```env
MODEL_NAME=custom-finetuned-model
USE_GPU=false
MAX_TOKENS=512
TEMPERATURE=0.1
```

## 🚨 Troubleshooting

### Common Issues
1. **Backend connection failed**
   - Ensure server is running: `python backend/main.py`
   - Check URL in extension settings

2. **Model loading errors**
   - Verify model file exists
   - Check available RAM (4GB+ recommended)

3. **YouTube integration issues**
   - Refresh the YouTube page
   - Check extension permissions

### Performance Tips
- Use GPU acceleration if available
- Close other memory-intensive applications
- Consider smaller model variants for limited hardware

## 🔐 Privacy & Security
- **Local processing**: All data stays on your machine
- **Custom fine-tuned model**: Optimized for your specific needs
- **Automatic cleanup**: Temporary files are removed
- **No tracking**: Extension doesn't collect personal data

## 🌟 Migration from Streamlit

### What Changed
- ✅ **Better UX**: Native YouTube integration
- ✅ **Performance**: Background processing
- ✅ **Persistence**: Saved summaries
- ✅ **Scalability**: API-based architecture
- ✅ **Cross-platform**: Works anywhere Chrome runs

### Legacy Support
The original Streamlit app (`yt_summary.py`) is still included for reference and can be run independently:
```bash
streamlit run yt_summary.py
```

## 🔗 API Endpoints

The backend provides:
- `GET /health` - Health check
- `POST /process-video` - Video analysis
- `GET /models/status` - AI model status
- `GET /docs` - Interactive documentation

## 🌟 Demo
[Extension Demo Video](https://www.youtube.com/watch?v=K9mDAb2Lz6Y) - Original concept demo

## 🔗 Resource Links:
- **Custom AI Models**: Advanced fine-tuning techniques
- **Chrome Extension Docs**: https://developer.chrome.com/docs/extensions/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Whisper Documentation**: https://openai.com/research/whisper

## 📊 Performance Metrics
- **Transcription**: ~2-5 minutes for 10-minute video
- **Summarization**: +30 seconds with custom fine-tuned model
- **Memory usage**: 4-8GB with full model
- **Storage**: ~1MB per hour of video content

## 🤝 Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License 
Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Acknowledgments
- OpenAI for Whisper
- FastAPI team
- Chrome Extension community
- Machine Learning research community

---

#### **⭐ If you like this Full-Stack Extension, please star the repo!**
#### Follow the developer: [![LinkedIn](https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ankeatacodes/) &nbsp; [![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ankeatacodes/)

---

---
