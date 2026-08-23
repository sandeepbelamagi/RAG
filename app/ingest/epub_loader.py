from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup
from ebooklib import ITEM_DOCUMENT, epub

from app.core.models import ExtractedPage, SourceDocument


def _metadata_text(book: epub.EpubBook, key: str) -> str | None:
    items = book.get_metadata("DC", key)
    if not items:
        return None
    value = items[0][0]
    text = str(value).strip()
    return text or None


def load_epub(path: str | Path) -> tuple[SourceDocument, list[ExtractedPage]]:
    epub_path = Path(path)
    book = epub.read_epub(str(epub_path))

    document = SourceDocument(
        document_id=epub_path.stem,
        source_path=str(epub_path),
        title=_metadata_text(book, "title"),
        author=_metadata_text(book, "creator"),
        metadata={
            "format": "epub",
        },
    )

    pages: list[ExtractedPage] = []
    page_number = 1
    for item in book.get_items_of_type(ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "lxml")
        text = soup.get_text("\n", strip=True)
        if not text.strip():
            continue
        pages.append(
            ExtractedPage(
                page_number=page_number,
                text=text,
                source_type="epub",
                metadata={
                    "source_path": str(epub_path),
                    "item_name": item.get_name(),
                    "item_title": getattr(item, "title", None),
                },
            )
        )
        page_number += 1

    return document, pages
