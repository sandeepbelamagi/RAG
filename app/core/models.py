from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExtractedPage:
    page_number: int
    text: str
    source_type: str = "pdf"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SourceDocument:
    document_id: str
    source_path: str
    title: str | None = None
    author: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DocumentChunk:
    chunk_id: str
    document_id: str
    text: str
    page_start: int | None = None
    page_end: int | None = None
    chapter: str | None = None
    section: str | None = None
    chunk_index: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ParsedDocument:
    document: SourceDocument
    pages: list[ExtractedPage]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RetrievedChunk:
    chunk: DocumentChunk
    score: float
    rank: int = 0
