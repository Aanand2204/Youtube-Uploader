# YouTube Auto-Uploader — AI-Powered Video Publishing Pipeline

A high-performance, modular automation system that processes video files and handles the entire YouTube publishing workflow using state-of-the-art local AI and the YouTube Data API v3.

![Project Preview](file:///C:/Users/aanan/.gemini/antigravity/brain/1202ec56-738e-4d46-8eb2-b5a2cfe6f4e2/youtube_uploader_ui_full_page_1774811251002.png)

## 🚀 Features

- **Automated AI Pipeline**: 
    1.  **Audio Extraction**: High-fidelity mono WAV extraction via FFmpeg.
    2.  **Transcription**: Local inference using OpenAI Whisper (Multi-language support).
    3.  **AI Metadata Generation**: Local LLM orchestration via Ollama (Mistral/LLaMA) to generate compelling YouTube titles, descriptions, and tags.
    4.  **YouTube Integration**: Secure OAuth 2.0 publishing with automatic token management.
- **Two-Phase Workflow**: Processes metadata first, allowing for human review and editing before final publishing.
- **Premium Frontend**:
    - Modern, responsive Dark Mode UI.
    - Real-time pipeline progress tracking.
    - Integrated AI Metadata Editor.
    - Live Log Streaming with auto-refresh.
- **Industrial Backend**:
    - **FastAPI**: Asynchronous, high-performance API.
    - **Pydantic Settings**: Robust environment-based configuration.
    - **Rotating Logs**: Centralized logging for debugging and audit.

---

## 📂 Architecture

The project follows a clean, modular architecture designed for maintainability and scale:

```text
OpenClaw_Intermediate/
├── main.py                     # Entry point (Uvicorn launcher)
├── app/                        # Backend Application Core
│   ├── app.py                  # FastAPI Application Factory
│   ├── api/                    # API Routing Layer
│   │   ├── system.py           # Health & Logging endpoints
│   │   └── video.py            # Process & Publish endpoints
│   ├── core/                   # Infrastructure
│   │   ├── config.py           # Pydantic Settings
│   │   ├── logger.py           # Standardized Logging
│   │   └── exceptions.py       # Pipeline-specific errors
│   ├── models/                 # Data schemas (Pydantic models)
│   ├── services/               # Logical Units (The "Heavy Lifters")
│   │   ├── orchestrator.py      # Pipeline Manager
│   │   ├── video_processor.py   # FFmpeg extraction
│   │   ├── transcriber.py       # Whisper Transcription
│   │   ├── metadata_generator.py # Ollama LLM integration
│   │   └── youtube_uploader.py  # YouTube API v3 service
│   └── utils/                  # Shared helpers (Filesystem, etc.)
├── static/                     # Frontend Assets
│   ├── index.html              # Main UI Entry Point (Single Page App)
│   ├── style.css               # Premium Design System (Standardized Tokens)
│   └── js/                     # Modular Frontend Logic (ES Modules)
│       ├── constants.js        # DOM Selectors & Endpoints
│       ├── api.js              # Backend Communication Service
│       ├── ui.js               # Reactive View Controller
│       ├── utils.js            # Shared Helpers
│       └── app.js              # Main Controller & State Management
└── logs/                       # Application Runtime Logs
```

---

## 🛠️ Prerequisites

### 1. System Dependencies
- **Python**: Version 3.11 or higher.
- **FFmpeg**: Required for audio processing. Must be available on your system `PATH`.
    - *Windows*: `choco install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html).

### 2. AI Infrastructure (Local)
- **Ollama**: Install from [ollama.ai](https://ollama.ai).
- **Models**: Pull the required models before starting:
    ```bash
    ollama pull mistral
    ```
- **Service**: Ensure the Ollama server is running (`ollama serve`).

### 3. Google Cloud Project
1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **YouTube Data API v3**.
3. Create **OAuth 2.0 Desktop Credentials**.
4. Save the JSON file as `credentials/client_secrets.json`.

---

## 📦 Installation

```bash
# 1. Clone & Enter
git clone <repo-url>
cd OpenClaw_Intermediate

# 2. Virtual Environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate # macOS/Linux

# 3. Dependencies
pip install -r requirements.txt

# 4. PyTorch (Whisper Backend)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 5. Environment
cp .env.example .env
# Edit .env to set your OLLAMA_MODEL or FFMPEG_PATH if necessary.
```

---

## 🚀 Running the System

```bash
python main.py
```

- **Web Interface**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 🔐 First-Run Authentication

On your very first upload, a browser window will automatically open for Google OAuth consent. After you authorize the app, the system will securely cache a token in `credentials/token.pickle`. **All future uploads will be fully headless and automated.**

---

## 📄 API Reference

### `POST /api/v1/process-video`
Transcribes a video and generates AI metadata suggestions.
- **Payload**: `Multipart/form-data` with `file`.
- **Returns**: `video_id`, `title`, `description`, `tags`, and `transcript_preview`.

### `POST /api/v1/publish-video`
Finalizes the publishing of a processed video to YouTube.
- **Payload**: `JSON` with `video_id`, `title`, `description`, and `tags`.
- **Returns**: `youtube_url` and success status.

---

## 🛡️ License

MIT License — Built with OpenClaw & Advanced Agentic Coding.
