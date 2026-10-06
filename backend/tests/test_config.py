import pytest

from app.config import get_llm_backend, get_vector_backend


def test_get_llm_backend_prefers_cloud_openai_when_local_ollama_is_disabled(monkeypatch):
    monkeypatch.delenv("LOCAL_OLLAMA", raising=False)
    monkeypatch.setenv("CLOUD_LLM", "openai")

    assert get_llm_backend() == "openai"


def test_get_vector_backend_prefers_pinecone_when_configured(monkeypatch):
    monkeypatch.setenv("VECTOR_DB", "pinecone")
    monkeypatch.setenv("PINECONE_API_KEY", "test-key")
    monkeypatch.setenv("PINECONE_INDEX", "demo-index")

    assert get_vector_backend() == "pinecone"
