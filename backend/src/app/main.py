from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import router
from app.config import get_allowed_origins
from app.utils.logging import configure_logging

env_path = Path(__file__).resolve().parents[3] / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path, override=False)

if os.getenv("LOCAL_OLLAMA", "false").lower() in {"1", "true", "yes", "on"}:
    if not os.getenv("OLLAMA_BASE_URL"):
        print("⚠️  WARNING: OLLAMA_BASE_URL not set in .env")
    if not os.getenv("OLLAMA_MODEL"):
        print("⚠️  WARNING: OLLAMA_MODEL not set in .env")
    if not os.getenv("OLLAMA_EMBEDDING_MODEL"):
        print("⚠️  WARNING: OLLAMA_EMBEDDING_MODEL not set in .env")
else:
    if not os.getenv("LLM_API_KEY"):
        print("⚠️  WARNING: LLM_API_KEY not set for cloud provider mode")

configure_logging()

app = FastAPI(
    title="IKMS RAG API",
    version="1.0.0",
    description="Evidence-Aware RAG System with PDF Indexing and Citation Support",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

allowed_origins = get_allowed_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Serve static files (HTML UI)
static_dir = Path(__file__).parent.parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "IKMS RAG API is running"}


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "qa": "/qa",
            "search": "/search",
            "index_pdf": "/index-pdf",
            "upload_pdf": "/upload-pdf",
            "docs": "/docs",
            "ui": "/static/index.html"
        }
    }
