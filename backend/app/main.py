from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(title="Sales Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
