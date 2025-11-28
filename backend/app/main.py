from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Sales Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize required NLP resources on startup."""
    try:
        import nltk
        # Ensure VADER lexicon is available
        try:
            nltk.data.find('sentiment/vader_lexicon')
            logger.info("✓ VADER lexicon found")
        except LookupError:
            logger.info("Downloading VADER lexicon for sentiment analysis...")
            nltk.download('vader_lexicon', quiet=True)
            logger.info("✓ VADER lexicon downloaded successfully")
    except Exception as e:
        logger.warning(f"Could not initialize NLTK resources: {e}")
    
    logger.info("Sales Copilot Backend initialized successfully")

@app.get("/")
async def root():
    return {"message": "Sales Copilot Backend Running"}

from app.api.websocket import router as websocket_router
from app.api.rag import router as rag_router
from app.api.analytics import router as analytics_router
from app.api.agents import router as agents_router

app.include_router(websocket_router)
app.include_router(rag_router)
app.include_router(analytics_router)
app.include_router(agents_router)
