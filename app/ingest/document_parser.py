from __future__ import annotations

from pathlib import Path

from app.core.models import ParsedDocument
from app.ingest.clean_text import clean_extracted_pages
from app.ingest.epub_loader import load_epub
from app.ingest.pdf_loader import load_pdf


SUPPORTED_EXTENSIONS = {".pdf", ".epub"}


def parse_document(path: str | Path, *, clean: bool = True) -> ParsedDocument:
    source_path = Path(path)
    extension = source_path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported document type: {source_path.suffix}")

    if extension == ".pdf":
        document, pages = load_pdf(source_path)
    else:
        document, pages = load_epub(source_path)

    if clean:
        pages = clean_extracted_pages(pages)

    metadata = {
        "source_path": str(source_path),
        "extension": extension,
        "page_count": len(pages),
        **document.metadata,
    }
    return ParsedDocument(document=document, pages=pages, metadata=metadata)

