"""
TubeMind API — Main Application
YouTube Video Intelligence Platform powered by RAG + Gemini

Run with: uvicorn app.main:app --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.session import init_db
from app.api.routes import health, videos, chat

# ──────────────────────────────────────────────
# Logging Configuration
# ──────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Application Lifespan
# ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 TubeMind API starting up...")
    logger.info(f"   Environment: {settings.ENVIRONMENT}")
    logger.info(f"   LLM Model: {settings.LLM_MODEL}")
    logger.info(f"   Embedding Model: {settings.EMBEDDING_MODEL}")

    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")

    # Validate Gemini API key
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your-gemini-api-key-here":
        logger.warning(
            "⚠️  GEMINI_API_KEY not set! "
            "Get a free key at https://aistudio.google.com/apikey"
        )

    yield

    logger.info("👋 TubeMind API shutting down...")


# ──────────────────────────────────────────────
# Application Factory
# ──────────────────────────────────────────────

app = FastAPI(
    title="TubeMind API",
    description=(
        "YouTube Video Intelligence Platform — "
        "Chat with any YouTube video using AI-powered RAG "
        "(Retrieval-Augmented Generation) with Google Gemini."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ──────────────────────────────────────────────
# Middleware
# ──────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

app.include_router(health.router)
app.include_router(videos.router)
app.include_router(chat.router)


# ──────────────────────────────────────────────
# Root Endpoint
# ──────────────────────────────────────────────

@app.get("/", tags=["root"])
async def root():
    """Root endpoint — API information."""
    return {
        "name": "TubeMind API",
        "version": "1.0.0",
        "description": "YouTube Video Intelligence Platform",
        "docs": "/docs",
        "health": "/health",
    }
