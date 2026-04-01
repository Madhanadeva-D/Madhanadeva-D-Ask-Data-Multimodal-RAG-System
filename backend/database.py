import logging
from typing import List, Optional

from pymilvus import connections, Collection
from langchain_community.vectorstores import Milvus
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from .config import cfg

logger = logging.getLogger(__name__)


class _Embedder:
    """Thin wrapper so SentenceTransformer satisfies LangChain's embedding interface."""

    def __init__(self):
        self._model = SentenceTransformer(cfg.EMBED_MODEL)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._model.encode(texts, show_progress_bar=False).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self._model.encode(text, show_progress_bar=False).tolist()


class VectorDB:
    def __init__(self):
        self._embedder = _Embedder()
        self._store: Optional[Milvus] = None
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=cfg.CHUNK_SIZE,
            chunk_overlap=cfg.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    # ── lifecycle ────────────────────────────────────────────────────────────

    def connect(self):
        try:
            connections.disconnect("default")
        except Exception:
            pass

        connections.connect("default", host=cfg.MILVUS_HOST, port=cfg.MILVUS_PORT, timeout=10)

        self._store = Milvus(
            embedding_function=self._embedder,
            collection_name=cfg.COLLECTION,
            connection_args={"host": cfg.MILVUS_HOST, "port": cfg.MILVUS_PORT},
            consistency_level="Bounded",
            auto_id=True,
            index_params={"index_type": "HNSW", "metric_type": "COSINE",
                          "params": {"M": 16, "efConstruction": 200}},
            search_params={"metric_type": "COSINE", "params": {"ef": 64}},
            drop_old=False,
        )
        logger.info(f"Milvus connected — collection: {cfg.COLLECTION}")

    def disconnect(self):
        try:
            connections.disconnect("default")
        except Exception:
            pass

    # ── write ────────────────────────────────────────────────────────────────

    def ingest(self, text: str, source: str) -> int:
        """Split text into chunks and store in Milvus. Returns chunk count."""
        if not self._store:
            raise RuntimeError("Not connected.")
        text = text.strip()
        if not text:
            return 0
        chunks = self._splitter.split_text(text)
        meta   = [{"source": source, "chunk_idx": i} for i in range(len(chunks))]
        self._store.add_texts(chunks, metadatas=meta)
        logger.info(f"Ingested {len(chunks)} chunks — {source}")
        return len(chunks)

    # ── read ─────────────────────────────────────────────────────────────────

    def search(self, query: str, k: int = None, threshold: float = None) -> list:
        """
        Return relevant docs.
        langchain_community Milvus doesn't implement _select_relevance_score_fn,
        so we use similarity_search_with_score and filter manually.
        Milvus COSINE returns distance; similarity = 1 - distance.
        """
        if not self._store:
            raise RuntimeError("Not connected.")

        k         = k or cfg.TOP_K
        threshold = threshold if threshold is not None else cfg.SCORE_THRESHOLD

        results = self._store.similarity_search_with_score(query, k=k)
        docs = [doc for doc, dist in results if (1 - dist) >= threshold]

        if not docs:
            docs = [doc for doc, _ in results]  # fallback: return top-k unfiltered

        return docs

    # ── delete ───────────────────────────────────────────────────────────────

    def delete(self, source: str) -> int:
        if not self._store:
            raise RuntimeError("Not connected.")
        col: Collection = self._store.col
        res = col.delete(f'source == "{source}"')
        logger.info(f"Deleted {res.delete_count} chunks — {source}")
        return res.delete_count

    # ── stats ─────────────────────────────────────────────────────────────────

    def stats(self) -> dict:
        if not self._store:
            return {"connected": False}
        try:
            col: Collection = self._store.col
            col.load()
            return {"connected": True, "collection": cfg.COLLECTION,
                    "vectors": col.num_entities}
        except Exception as e:
            return {"connected": True, "error": str(e)}
