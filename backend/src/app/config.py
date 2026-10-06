import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env", override=False)


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def get_llm_backend() -> str:
    if _as_bool(os.getenv("LOCAL_OLLAMA"), False):
        return "ollama"

    configured = (os.getenv("CLOUD_LLM") or "openai").strip().lower()
    return configured or "openai"


def get_vector_backend() -> str:
    configured = (os.getenv("VECTOR_DB") or "pinecone").strip().lower()

    if configured == "pinecone":
        if os.getenv("PINECONE_API_KEY") and os.getenv("PINECONE_INDEX"):
            return "pinecone"
        return "local"

    if configured == "local":
        return "local"

    return configured


def get_allowed_origins() -> list[str]:
    values = _split_csv(os.getenv("FRONTEND_ORIGIN"))
    values.extend(_split_csv(os.getenv("ALLOWED_ORIGINS")))

    if not values:
        values = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://localhost:4173",
        ]

    return list(dict.fromkeys(values))
