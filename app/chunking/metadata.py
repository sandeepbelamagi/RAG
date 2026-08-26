from __future__ import annotations

import hashlib
from typing import Any

from app.core.models import DocumentChunk, ParsedDocument


def stable_chunk_id(document_id: str, chunk_index: int, text: str) -> str:
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
    return f"{document_id}:{chunk_index}:{digest}"


def build_chunk_metadata(
    parsed_document: ParsedDocument,
    *,
    chunk_index: int,
    page_start: int | None,
    page_end: int | None,
    chapter: str | None = None,
    section: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "document_id": parsed_document.document.document_id,
        "source_path": parsed_document.document.source_path,
        "book_title": parsed_document.document.title,
        "author": parsed_document.document.author,
        "chunk_index": chunk_index,
        "page_start": page_start,
        "page_end": page_end,
        "chapter": chapter,
        "section": section,
    }
    if extra:
        metadata.update(extra)
    return metadata


def make_chunk(
    parsed_document: ParsedDocument,
    *,
    chunk_index: int,
    text: str,
    page_start: int | None,
    page_end: int | None,
    chapter: str | None = None,
    section: str | None = None,
    extra: dict[str, Any] | None = None,
) -> DocumentChunk:
    metadata = build_chunk_metadata(
        parsed_document,
        chunk_index=chunk_index,
        page_start=page_start,
        page_end=page_end,
        chapter=chapter,
        section=section,
        extra=extra,
    )
    return DocumentChunk(
        chunk_id=stable_chunk_id(parsed_document.document.document_id, chunk_index, text),
        document_id=parsed_document.document.document_id,
        text=text,
        page_start=page_start,
        page_end=page_end,
        chapter=chapter,
        section=section,
        chunk_index=chunk_index,
        metadata=metadata,
    )

