from __future__ import annotations

from dataclasses import dataclass

from app.core.models import DocumentChunk, ParsedDocument
from app.chunking.metadata import make_chunk


@dataclass(slots=True)
class FixedChunkingConfig:
    chunk_size_words: int = 220
    overlap_words: int = 40

    def __post_init__(self) -> None:
        if self.chunk_size_words <= 0:
            raise ValueError("chunk_size_words must be positive")
        if self.overlap_words < 0:
            raise ValueError("overlap_words cannot be negative")
        if self.overlap_words >= self.chunk_size_words:
            raise ValueError("overlap_words must be smaller than chunk_size_words")


def _split_words(text: str) -> list[str]:
    return [word for word in text.split() if word]


def chunk_parsed_document_fixed(
    parsed_document: ParsedDocument,
    config: FixedChunkingConfig | None = None,
) -> list[DocumentChunk]:
    config = config or FixedChunkingConfig()
    chunks: list[DocumentChunk] = []

    for page in parsed_document.pages:
        words = _split_words(page.text)
        if not words:
            continue

        start = 0
        local_index = 0
        step = config.chunk_size_words - config.overlap_words
        while start < len(words):
            end = min(start + config.chunk_size_words, len(words))
            chunk_text = " ".join(words[start:end]).strip()
            if chunk_text:
                chunks.append(
                    make_chunk(
                        parsed_document,
                        chunk_index=len(chunks),
                        text=chunk_text,
                        page_start=page.page_number,
                        page_end=page.page_number,
                        extra={
                            "strategy": "fixed",
                            "local_index": local_index,
                            "source_type": page.source_type,
                        },
                    )
                )
                local_index += 1
            if end >= len(words):
                break
            start += step

    return chunks

