import logging
from pathlib import Path
from functools import lru_cache
from urllib.error import URLError
from urllib.request import urlopen

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.schemas import (
    CitationResponse,
    HealthResponse,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    ReadinessResponse,
    RetrievedSourceResponse,
)
from app.api.service import RAGService, build_rag_service
from app.core.config import get_settings


router = APIRouter()
logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    return build_rag_service(get_settings())


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", app_name=settings.app_name, environment=settings.app_env)


@router.get("/ready", response_model=ReadinessResponse)
def ready() -> ReadinessResponse:
    settings = get_settings()
    chroma_status = "ok" if Path(settings.chroma_persist_dir).exists() else "unavailable"
    ollama_status = "unavailable"
    try:
        with urlopen(f"{settings.ollama_base_url.rstrip('/')}/api/tags", timeout=2) as response:
            ollama_status = "ok" if response.status == 200 else "unavailable"
    except (OSError, URLError):
        pass
    status_value = "ok" if chroma_status == "ok" and ollama_status == "ok" else "not_ready"
    return ReadinessResponse(status=status_value, ollama=ollama_status, chroma=chroma_status)


@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest(
    file: UploadFile = File(...),
    strategy: str = Form(default="semantic"),
    service: RAGService = Depends(get_rag_service),
) -> IngestResponse:
    filename = Path(file.filename or "").name
    if Path(filename).suffix.lower() not in {".pdf", ".epub"}:
        raise HTTPException(status_code=400, detail="Only PDF and EPUB files are supported")

    settings = get_settings()
    try:
        content = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
        if len(content) > settings.max_upload_mb * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Uploaded file is too large")
        destination = Path(settings.upload_dir) / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        chunks_indexed = service.ingest(destination, strategy=strategy)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Ingestion failed for %s", filename)
        raise HTTPException(status_code=500, detail="Document ingestion failed") from exc
    return IngestResponse(filename=filename, strategy=strategy, chunks_indexed=chunks_indexed)


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest, service: RAGService = Depends(get_rag_service)) -> QueryResponse:
    try:
        result = service.query(request.question, k=request.k, book_title=request.book_title)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Query failed")
        raise HTTPException(status_code=500, detail="Query failed") from exc

    citations = [
        CitationResponse(
            marker=citation.marker,
            title=citation.title,
            page_start=citation.page_start,
            page_end=citation.page_end,
            chunk_id=citation.chunk_id,
        )
        for citation in result.generated.citations
    ]
    sources = [
        RetrievedSourceResponse(
            chunk_id=item.chunk.chunk_id,
            score=item.score,
            text=item.chunk.text,
            title=item.chunk.metadata.get("book_title"),
            page_start=item.chunk.page_start,
            page_end=item.chunk.page_end,
        )
        for item in result.retrieved
    ]
    return QueryResponse(
        answer=result.generated.answer,
        grounded=result.generated.grounded,
        confidence=result.generated.confidence,
        citations=citations,
        sources=sources,
    )
