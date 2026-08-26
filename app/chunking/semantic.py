from __future__ import annotations

import re
from dataclasses import dataclass

from app.chunking.metadata import make_chunk
from app.core.models import DocumentChunk, ParsedDocument


_CHAPTER_RE = re.compile(r"^(chapter|chap\.)\s+(.+)$", re.IGNORECASE)
_SECTION_RE = re.compile(r"^(\d+(?:\.\d+)*)\s+(.+)$")
_HEADING_RE = re.compile(r"^(?:[A-Z][A-Za-z0-9 ,:\-]{2,80}|[A-Z0-9][A-Z0-9 ,:\-]{2,80})$")


@dataclass(slots=True)
class SectionBlock:
    chapter: str | None
    section: str | None
    page_start: int
    page_end: int
    lines: list[str]


def _looks_like_heading(line: str) -> bool:
    stripped = line.strip()
    if len(stripped) < 3 or len(stripped) > 90:
        return False
    if _CHAPTER_RE.match(stripped) or _SECTION_RE.match(stripped):
        return True
    if stripped.isupper():
        return True
    if _HEADING_RE.match(stripped) and len(stripped.split()) <= 8:
        return True
    return False


def _extract_labels(line: str) -> tuple[str | None, str | None]:
    stripped = line.strip()
    chapter_match = _CHAPTER_RE.match(stripped)
    if chapter_match:
        return f"Chapter {chapter_match.group(2).strip()}", None

    section_match = _SECTION_RE.match(stripped)
    if section_match:
        return None, f"{section_match.group(1)} {section_match.group(2).strip()}"

    if stripped.isupper() or _HEADING_RE.match(stripped):
        return None, stripped

    return None, None


def _collect_blocks(parsed_document: ParsedDocument) -> list[SectionBlock]:
    blocks: list[SectionBlock] = []
    current_lines: list[str] = []
    current_chapter: str | None = None
    current_section: str | None = None
    current_start_page: int | None = None
    current_end_page: int | None = None

    def flush() -> None:
        nonlocal current_lines, current_start_page, current_end_page
        if current_lines and current_start_page is not None and current_end_page is not None:
            blocks.append(
                SectionBlock(
                    chapter=current_chapter,
                    section=current_section,
                    page_start=current_start_page,
                    page_end=current_end_page,
                    lines=current_lines[:],
                )
            )
        current_lines = []
        current_start_page = None
        current_end_page = None

    for page in parsed_document.pages:
        for raw_line in page.text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if _looks_like_heading(line):
                label_chapter, label_section = _extract_labels(line)
                if current_lines:
                    flush()
                if label_chapter is not None:
                    current_chapter = label_chapter
                    current_section = None
                if label_section is not None:
                    current_section = label_section
                continue

            if current_start_page is None:
                current_start_page = page.page_number
            current_end_page = page.page_number
            current_lines.append(line)

    flush()
    return blocks


def chunk_parsed_document_semantic(
    parsed_document: ParsedDocument,
    *,
    max_words_per_chunk: int = 260,
) -> list[DocumentChunk]:
    if max_words_per_chunk <= 0:
        raise ValueError("max_words_per_chunk must be positive")

    blocks = _collect_blocks(parsed_document)
    chunks: list[DocumentChunk] = []

    for block in blocks:
        words = " ".join(block.lines).split()
        if not words:
            continue

        start = 0
        while start < len(words):
            end = min(start + max_words_per_chunk, len(words))
            text = " ".join(words[start:end]).strip()
            if text:
                chunks.append(
                    make_chunk(
                        parsed_document,
                        chunk_index=len(chunks),
                        text=text,
                        page_start=block.page_start,
                        page_end=block.page_end,
                        chapter=block.chapter,
                        section=block.section,
                        extra={
                            "strategy": "semantic",
                            "block_word_start": start,
                        },
                    )
                )
            start = end

    return chunks

