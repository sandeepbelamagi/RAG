from pathlib import Path

import pytest

from app.core.models import ExtractedPage, ParsedDocument, SourceDocument
from app.ingest import document_parser


def test_parse_document_dispatches_pdf(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    path = tmp_path / "book.pdf"
    path.write_text("")

    def fake_load_pdf(_: Path):
        return (
            SourceDocument(document_id="book", source_path=str(path), title="Book"),
            [ExtractedPage(page_number=1, text="content", source_type="pdf")],
        )

    monkeypatch.setattr(document_parser, "load_pdf", fake_load_pdf)

    parsed = document_parser.parse_document(path, clean=False)
    assert isinstance(parsed, ParsedDocument)
    assert parsed.document.title == "Book"
    assert parsed.pages[0].text == "content"


def test_parse_document_rejects_unknown_extension(tmp_path: Path) -> None:
    path = tmp_path / "book.txt"
    path.write_text("not supported")

    with pytest.raises(ValueError, match="Unsupported document type"):
        document_parser.parse_document(path)

