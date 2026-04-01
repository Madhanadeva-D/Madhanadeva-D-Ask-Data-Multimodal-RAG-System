import logging
from contextlib import asynccontextmanager
from io import BytesIO

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import cfg
from .database import VectorDB
from .generator import Generator
from .extractor import from_url, from_pdf, from_image

logging.basicConfig(
    level=logging.DEBUG if cfg.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

_SUPPORTED = {"pdf", "png", "jpg", "jpeg", "tiff", "bmp", "webp"}

db  = VectorDB()
gen = Generator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.connect()
    logger.info("Startup complete.")
    yield
    db.disconnect()


app = FastAPI(title="Multimodal RAG", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── schemas ───────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question:        str
    top_k:           int   = cfg.TOP_K
    score_threshold: float = cfg.SCORE_THRESHOLD


# ── /health ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return db.stats()


# ── /load ─────────────────────────────────────────────────────────────────────

@app.post("/load")
async def load(
    url:  str        = Query(default=None, description="Web URL to scrape"),
    file: UploadFile = File(default=None,  description="PDF or image file"),
):
    """
    Load data into Milvus from a URL or an uploaded file.
    Provide exactly one of: ?url=... or a multipart file.
    """
    # ── URL ──
    if url:
        try:
            text = from_url(url.strip())
        except Exception as e:
            raise HTTPException(400, f"URL extraction failed: {e}")
        if not text:
            raise HTTPException(422, "No text extracted from URL.")
        chunks = db.ingest(text, source=f"url:{url.strip()}")
        return {"source": f"url:{url.strip()}", "chunks": chunks}

    # ── File ──
    if file:
        ext = (file.filename or "").rsplit(".", 1)[-1].lower()
        if ext not in _SUPPORTED:
            raise HTTPException(415, f"Unsupported type '.{ext}'.")

        raw = await file.read()
        if not raw:
            raise HTTPException(400, "Empty file.")
        if len(raw) > cfg.MAX_FILE_MB * 1024 * 1024:
            raise HTTPException(413, f"File exceeds {cfg.MAX_FILE_MB} MB.")

        try:
            if ext == "pdf":
                text        = from_pdf(BytesIO(raw))
                source_type = "pdf"
            else:
                text        = from_image(BytesIO(raw))
                source_type = "image"
        except Exception as e:
            raise HTTPException(400, f"Extraction failed: {e}")

        if not text:
            raise HTTPException(422, "No text extracted from file.")

        chunks = db.ingest(text, source=f"{source_type}:{file.filename}")
        return {"source": f"{source_type}:{file.filename}", "chunks": chunks}

    raise HTTPException(400, "Provide ?url=... or upload a file.")


# ── /query ────────────────────────────────────────────────────────────────────

@app.post("/query")
def query(req: QueryRequest):
    """Retrieve relevant docs and generate an answer via Nemotron."""
    docs = db.search(req.question, k=req.top_k, threshold=req.score_threshold)

    try:
        answer = gen.generate(req.question, docs)
    except RuntimeError as e:
        raise HTTPException(503, str(e))

    sources    = list({d.metadata.get("source", "unknown") for d in docs})
    confidence = round(min(0.99, len(docs) / max(cfg.TOP_K, 1)), 4)

    return {"answer": answer, "sources": sources, "confidence": confidence}


# ── /delete ───────────────────────────────────────────────────────────────────

@app.delete("/delete")
def delete(source: str = Query(..., description="Source ID to remove")):
    """Delete all chunks belonging to a source."""
    count = db.delete(source)
    return {"deleted": count, "source": source}
