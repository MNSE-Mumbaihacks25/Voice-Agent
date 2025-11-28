# Backend Setup Guide

## Installation

### 1. Prerequisites
- Python 3.13+
- Virtual environment (recommended)

### 2. Install Dependencies

```bash
# From the project root
pip install -r requirements.txt

# OR using pyproject.toml
pip install -e .
```

### 3. Download NLP Data (OPTIONAL - will auto-download on first run)

If you want to pre-download NLTK data before starting the app:

```bash
cd backend
python setup_nltk.py
```

Or manually:
```bash
python -c "import nltk; nltk.download('vader_lexicon')"
```

### 4. Environment Variables

Create a `.env` file in the backend directory with:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
DEEPGRAM_API_KEY=your_deepgram_key
GROQ_API_KEY=your_groq_key
OPENROUTER_EMBEDDING_KEY=your_openrouter_key
GOOGLE_API_KEY=your_google_key
```

### 5. Run the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The backend will be available at `http://localhost:8000`

## Features

### Transcription Engines
- **Whisper (Default)**: Local, offline-capable speech-to-text using OpenAI's Whisper model
- **Deepgram**: Cloud-based transcription with speaker diarization

### Real-time Analysis
- **Speaker Identification**: Automatic speaker detection based on audio fingerprints
- **Sentiment Analysis**: Detects Positive, Negative, Anger, Sarcasm, and Neutral tones
- **Profanity Detection**: Flags potentially inappropriate language
- **Audio Fingerprinting**: Energy and frequency-based speaker identification

### WebSocket Endpoints

#### `/ws/audio`
Bidirectional WebSocket for live audio streaming and transcription.

**Query Parameters:**
- `session_id` (required): Unique session identifier
- `agent_name` (optional, default: "Agent"): Name of the speaking agent
- `lead_name` (optional, default: "Lead"): Name of the lead/customer
- `language` (optional, default: "en"): Language code (en, hi, mr, etc.)
- `engine` (optional, default: "whisper"): Transcription engine ("whisper" or "deepgram")

**Example:**
```
ws://localhost:8000/ws/audio?session_id=abc123&agent_name=John&lead_name=Karen&language=en&engine=whisper
```

**Response Format:**
```json
{
  "type": "transcript",
  "data": "transcribed text",
  "speaker": 0,
  "speaker_name": "Speaker 1",
  "is_final": true,
  "sentiment": "Positive",
  "profanity_detected": false,
  "timestamp": "2025-11-29T03:58:05.756348Z"
}
```

## Architecture

### Services

- **`whisper_service.py`**: Local Whisper-based transcription with sentiment analysis and speaker diarization
- **`deepgram_service.py`**: Cloud-based Deepgram transcription
- **`rag_service.py`**: Retrieval-Augmented Generation for knowledge base queries
- **`summary_service.py`**: Call summarization using LLMs
- **`agent_service.py`**: Agent and lead management
- **`analytics_service.py`**: Call analytics and reporting

### Models

- **Whisper Base (base.en)**: ~147MB, fast, suitable for real-time transcription
- Supports: tiny, small, medium, large models for different performance/accuracy trade-offs

## Troubleshooting

### NLTK VADER Lexicon Error
If you see: `Resource vader_lexicon not found`

The app will automatically download it on startup. If you want to pre-download:
```bash
python setup_nltk.py
```

### Port Already in Use
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

### WebSocket Connection Issues
- Ensure CORS is properly configured
- Check that the frontend is connecting to the correct backend URL
- Verify firewall/network settings allow WebSocket connections

### Memory Issues with Whisper
- Use `tiny.en` model for lower memory usage
- Adjust `n_threads` parameter in WhisperService initialization
- Consider using Deepgram for resource-constrained environments

## Performance Tips

1. **Chunking**: Audio is processed in 8000-byte chunks (250ms at 16kHz) for low-latency streaming
2. **Threading**: Default 6 CPU threads for Whisper - adjust based on your hardware
3. **Buffer Management**: Transcription triggered every ~5 seconds of audio for responsive feedback
4. **Speaker Detection**: Lightweight fingerprint-based approach with minimal overhead

## API Endpoints

### POST `/assist`
Get RAG assistance based on current transcript

**Body:**
```json
{
  "session_id": "abc123"
}
```

### POST `/end-call`
End call and generate analytics report

**Body:**
```json
{
  "session_id": "abc123"
}
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Structure
```
app/
├── main.py                 # FastAPI app initialization
├── api/
│   ├── websocket.py       # WebSocket endpoints
│   ├── rag.py            # RAG endpoints
│   ├── agents.py         # Agent management
│   └── analytics.py      # Analytics endpoints
├── services/
│   ├── whisper_service.py      # Whisper transcription
│   ├── deepgram_service.py     # Deepgram integration
│   ├── rag_service.py          # RAG logic
│   ├── summary_service.py      # Summarization
│   ├── agent_service.py        # Agent logic
│   └── analytics_service.py    # Analytics logic
└── core/
    ├── config.py         # Settings and configuration
    └── state.py          # Global state management
```
