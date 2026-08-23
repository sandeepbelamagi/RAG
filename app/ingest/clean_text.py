from __future__ import annotations

import re
import unicodedata
from collections import Counter

from app.core.models import ExtractedPage


_HYPHENATED_LINE_END = re.compile(r"(\w)-\n(\w)")
_MULTIPLE_NEWLINES = re.compile(r"\n{3,}")
_MULTIPLE_SPACES = re.compile(r"[ \t]{2,}")
_PAGE_NUMBER_ONLY = re.compile(r"^\s*\d+\s*$")
_FOLIO_ONLY = re.compile(r"^\s*(?:page\s*)?\d+\s*$", re.IGNORECASE)


def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def dehyphenate_line_breaks(text: str) -> str:
    return _HYPHENATED_LINE_END.sub(r"\1\2", text)


def collapse_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)
    text = _MULTIPLE_SPACES.sub(" ", text)
    text = _MULTIPLE_NEWLINES.sub("\n\n", text)
    return text.strip()


def strip_boilerplate_lines(lines: list[str], remove_candidates: set[str]) -> list[str]:
    cleaned: list[str] = []
    for line in lines:
        normalized = line.strip()
        if not normalized:
            cleaned.append("")
            continue
        if normalized in remove_candidates:
            continue
        if _PAGE_NUMBER_ONLY.match(normalized):
            continue
        if _FOLIO_ONLY.match(normalized):
            continue
        cleaned.append(normalized)
    return cleaned


def _candidate_boilerplate_lines(pages: list[ExtractedPage], top_n: int = 2, bottom_n: int = 2) -> set[str]:
    counts: Counter[str] = Counter()
    page_count = 0
    for page in pages:
        lines = [line.strip() for line in page.text.splitlines() if line.strip()]
        if not lines:
            continue
        page_count += 1
        for line in lines[:top_n]:
            counts[line] += 1
        for line in lines[-bottom_n:]:
            counts[line] += 1
    threshold = max(2, int(page_count * 0.6))
    return {line for line, count in counts.items() if count >= threshold}


def clean_page_text(text: str) -> str:
    text = normalize_unicode(text)
    text = dehyphenate_line_breaks(text)
    text = text.replace("\u00ad", "")
    text = text.replace("\x0c", "\n")
    text = collapse_whitespace(text)
    return text


def clean_extracted_pages(pages: list[ExtractedPage]) -> list[ExtractedPage]:
    boilerplate = _candidate_boilerplate_lines(pages)
    cleaned_pages: list[ExtractedPage] = []
    for page in pages:
        lines = page.text.splitlines()
        lines = strip_boilerplate_lines(lines, boilerplate)
        text = "\n".join(lines)
        text = clean_page_text(text)
        cleaned_pages.append(
            ExtractedPage(
                page_number=page.page_number,
                text=text,
                source_type=page.source_type,
                metadata=dict(page.metadata),
            )
        )
    return cleaned_pages
