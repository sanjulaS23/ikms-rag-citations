import os
from pathlib import Path

from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import get_env_value, get_llm_backend, get_vector_backend
from app.utils.logging import get_logger


logger = get_logger(__name__)


def get_embeddings():
    if get_llm_backend() == "ollama":
        try:
            from langchain_ollama import OllamaEmbeddings
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "LOCAL_OLLAMA=true but langchain_ollama is not installed. "
                "Install the local Ollama dependencies for development mode."
            ) from exc

        model = get_env_value("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text:latest")
        base_url = get_env_value("OLLAMA_BASE_URL", "http://localhost:11434")
        return OllamaEmbeddings(model=model, base_url=base_url)

    api_key = get_env_value("GEMINI_API_KEY")
    if not api_key:
     raise RuntimeError("GEMINI_API_KEY is required for Gemini embeddings.")

    return GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-2",
    google_api_key=api_key,
    output_dimensionality=3072,
)


class LocalVectorStore:
    """Simple local FAISS-backed vector store using Ollama embeddings."""

    def __init__(self, embeddings, index_dir: Path):
        self.embeddings = embeddings
        self.index_dir = index_dir
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.store = self._load_store()

    def _load_store(self):
        try:
            from langchain_community.vectorstores import FAISS
        except ImportError as exc:
            raise RuntimeError("langchain-community must be installed for FAISS support") from exc

        candidates = [self.index_dir, self.index_dir / "index"]
        index_dir = next(
            (
                p
                for p in candidates
                if p.exists() and ((p / "index.faiss").exists() or (p / "index.pkl").exists())
            ),
            None,
        )

        if index_dir is None:
            logger.info("No FAISS index found at %s", self.index_dir)
            return None

        try:
            return FAISS.load_local(str(index_dir), self.embeddings, allow_dangerous_deserialization=True)
        except Exception as exc:
            logger.warning("Could not load FAISS index at %s: %s", index_dir, exc)
            return None

    def add_texts(self, texts, metadatas=None, namespace=None):
        if not texts:
            return 0

        try:
            from langchain_community.vectorstores import FAISS
        except ImportError as exc:
            raise RuntimeError("langchain-community must be installed for FAISS support") from exc

        metadata_list = metadatas or [{} for _ in texts]
        docs = [
            Document(page_content=text, metadata=meta or {})
            for text, meta in zip(texts, metadata_list)
        ]

        if self.store is None:
            self.store = FAISS.from_documents(docs, self.embeddings)
        else:
            self.store.add_documents(docs)

        self.store.save_local(str(self.index_dir))
        return len(texts)

    def similarity_search(self, query, k=4, **kwargs):
        if self.store is None:
            return []
        return self.store.similarity_search(query, k=k, **kwargs)


class PineconeVectorStoreAdapter:
    """Thin wrapper around a cloud Pinecone vectorstore."""

    def __init__(self, embeddings, namespace: str | None = None):
        self.embeddings = embeddings
        self.namespace = namespace or get_env_value("PINECONE_NAMESPACE", "default")
        self.store = self._build_store()

    def _build_store(self):
        try:
            from langchain_pinecone import PineconeVectorStore
            from pinecone import Pinecone
        except ImportError as exc:
            raise RuntimeError("Pinecone dependencies are missing from the backend environment") from exc

        api_key = get_env_value("PINECONE_API_KEY")
        index_name = get_env_value("PINECONE_INDEX")
        if not api_key or not index_name:
            raise RuntimeError("PINECONE_API_KEY and PINECONE_INDEX must be configured for cloud vector storage.")

        client = Pinecone(api_key=api_key)
        index = client.Index(index_name)
        return PineconeVectorStore(index=index, embedding=self.embeddings, text_key="text", namespace=self.namespace)

    def add_texts(self, texts, metadatas=None, namespace=None):
        if not texts:
            return 0

        docs = [
            Document(page_content=text, metadata=meta or {})
            for text, meta in zip(texts, metadatas or [{} for _ in texts])
        ]
        self.store.add_documents(docs)
        return len(texts)

    def similarity_search(self, query, k=4, **kwargs):
        return self.store.similarity_search(query, k=k, namespace=self.namespace, **kwargs)


def get_vectorstore():
    """Create or load a vectorstore based on the configured backend."""
    backend = get_vector_backend()

    if backend == "pinecone":
        logger.info("Using Pinecone vector store")
        return PineconeVectorStoreAdapter(embeddings=get_embeddings())

    try:
        from langchain_ollama import OllamaEmbeddings
    except ModuleNotFoundError as exc:
        logger.error("Ollama embeddings library not installed: %s", exc)
        raise RuntimeError(
            "LOCAL_OLLAMA=true but langchain_ollama is not installed. "
            "Install the local Ollama dependencies for development mode."
        ) from exc

    embedding_model = get_env_value("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text:latest")
    base_url = get_env_value("OLLAMA_BASE_URL", "http://localhost:11434")
    embeddings = OllamaEmbeddings(model=embedding_model, base_url=base_url)

    project_root = Path(__file__).resolve().parents[5]
    index_dir = project_root / ".faiss_store"

    logger.info(
        "Using local FAISS vector store at %s with Ollama embedding model %s",
        index_dir,
        embedding_model,
    )
    return LocalVectorStore(embeddings=embeddings, index_dir=index_dir)
