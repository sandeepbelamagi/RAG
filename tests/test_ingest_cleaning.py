from app.core.models import ExtractedPage
from app.ingest.clean_text import clean_extracted_pages, clean_page_text, dehyphenate_line_breaks


def test_dehyphenate_line_breaks() -> None:
    assert dehyphenate_line_breaks("inter-\nnal") == "internal"


def test_clean_page_text_collapses_whitespace() -> None:
    text = "  Hello   world  \r\n\r\nThis is   a test.  "
    assert clean_page_text(text) == "Hello world\n\nThis is a test."


def test_clean_extracted_pages_removes_repeated_headers_and_footers() -> None:
    pages = [
        ExtractedPage(page_number=1, text="Book Title\nChapter 1\nBody one\n1", source_type="pdf"),
        ExtractedPage(page_number=2, text="Book Title\nChapter 1\nBody two\n2", source_type="pdf"),
        ExtractedPage(page_number=3, text="Book Title\nChapter 1\nBody three\n3", source_type="pdf"),
    ]

    cleaned = clean_extracted_pages(pages)

    assert cleaned[0].text == "Body one"
    assert cleaned[1].text == "Body two"
    assert cleaned[2].text == "Body three"

