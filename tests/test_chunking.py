from app.chunking import FixedChunkingConfig, chunk_parsed_document_fixed, chunk_parsed_document_semantic
from app.core.models import ExtractedPage, ParsedDocument, SourceDocument


def _make_parsed_document() -> ParsedDocument:
    document = SourceDocument(
        document_id="book-1",
        source_path="/tmp/book.pdf",
        title="Test Book",
        author="Ada",
    )
    pages = [
        ExtractedPage(
            page_number=1,
            text="Intro heading\nThis is a simple test book with enough words to force chunking.\nChapter 1\nBody text one continues here with extra words for testing.",
            source_type="pdf",
        ),
        ExtractedPage(
            page_number=2,
            text="Chapter 2\nAnother section with more content and enough words to verify semantic chunking behavior.",
            source_type="pdf",
        ),
    ]
    return ParsedDocument(document=document, pages=pages)


def test_fixed_chunking_creates_overlapping_chunks() -> None:
    parsed = _make_parsed_document()
    chunks = chunk_parsed_document_fixed(parsed, FixedChunkingConfig(chunk_size_words=8, overlap_words=2))

    assert len(chunks) >= 2
    assert chunks[0].metadata["strategy"] == "fixed"
    assert chunks[0].page_start == 1
    assert chunks[0].page_end == 1
    assert chunks[0].metadata["book_title"] == "Test Book"
    first_words = chunks[0].text.split()
    second_words = chunks[1].text.split()
    assert first_words[-2:] == second_words[:2]


def test_semantic_chunking_preserves_headings() -> None:
    parsed = _make_parsed_document()
    chunks = chunk_parsed_document_semantic(parsed, max_words_per_chunk=20)

    assert len(chunks) >= 2
    assert chunks[0].metadata["strategy"] == "semantic"
    assert any(chunk.chapter == "Chapter 1" for chunk in chunks)
    assert any(chunk.chapter == "Chapter 2" for chunk in chunks)
