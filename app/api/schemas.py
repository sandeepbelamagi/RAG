from pydantic import BaseModel
from pydantic import Field


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str


class ReadinessResponse(BaseModel):
    status: str
    ollama: str
    chroma: str


class IngestResponse(BaseModel):
    filename: str
    strategy: str
    chunks_indexed: int


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    k: int = Field(default=5, ge=1, le=50)
    book_title: str | None = None


class CitationResponse(BaseModel):
    marker: int
    title: str
    page_start: int | None
    page_end: int | None
    chunk_id: str


class RetrievedSourceResponse(BaseModel):
    chunk_id: str
    score: float
    text: str
    title: str | None = None
    page_start: int | None = None
    page_end: int | None = None


class QueryResponse(BaseModel):
    answer: str
    grounded: bool
    confidence: float
    citations: list[CitationResponse]
    sources: list[RetrievedSourceResponse]
