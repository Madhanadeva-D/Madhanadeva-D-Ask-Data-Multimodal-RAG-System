import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


class Config:
    # Milvus
    MILVUS_HOST: str = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT: str = os.getenv("MILVUS_PORT", "19530")
    COLLECTION:  str = os.getenv("COLLECTION_NAME", "rag_docs")

    # Embedding
    EMBED_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    EMBED_DIM:   int = int(os.getenv("EMBEDDING_DIM", 384))

    # Chunking
    CHUNK_SIZE:    int = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 150))

    # Retrieval
    TOP_K:           int   = int(os.getenv("TOP_K", 4))
    SCORE_THRESHOLD: float = float(os.getenv("SCORE_THRESHOLD", 0.3))

    # OpenRouter / Nemotron
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_MODEL:   str = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")
    LLM_TEMPERATURE:  float = float(os.getenv("LLM_TEMPERATURE", 0.3))
    LLM_MAX_TOKENS:     int = int(os.getenv("LLM_MAX_TOKENS", 512))

    # Misc
    MAX_FILE_MB: int = int(os.getenv("MAX_FILE_MB", 20))
    DEBUG:      bool = os.getenv("DEBUG", "false").lower() == "true"


cfg = Config()
