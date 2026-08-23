from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from app.core.models import ExtractedPage, SourceDocument


def _safe_metadata_value(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def load_pdf(path: str | Path) -> tuple[SourceDocument, list[ExtractedPage]]:
    pdf_path = Path(path)
    reader = PdfReader(str(pdf_path))
    metadata = reader.metadata or {}

    document = SourceDocument(
        document_id=pdf_path.stem,
        source_path=str(pdf_path),
        title=_safe_metadata_value(metadata.get("/Title")) if hasattr(metadata, "get") else None,
        author=_safe_metadata_value(metadata.get("/Author")) if hasattr(metadata, "get") else None,
        metadata={
            "format": "pdf",
            "page_count": len(reader.pages),
        },
    )

    pages: list[ExtractedPage] = []
    for index, page in enumerate(reader.pages, start=1):
        extracted = page.extract_text() or ""
        pages.append(
            ExtractedPage(
                page_number=index,
                text=extracted,
                source_type="pdf",
                metadata={"source_path": str(pdf_path)},
            )
        )

    return document, pages

