from app.api.service import RAGService
from app.core.models import DocumentChunk, RetrievedChunk
from app.generation.generator import GeneratedAnswer, SourceCitation


def test_service_query_passes_book_filter_and_returns_pipeline_result():
    class FakeRetriever:
        def retrieve(self, question, *, k, where):
            assert question == "What is attention?"
            assert k == 3
            assert where == {"book_title": "Book"}
            return [
                RetrievedChunk(
                    DocumentChunk("chunk-1", "doc-1", "attention text", metadata={"book_title": "Book"}),
                    0.9,
                    1,
                )
            ]

    class FakeGenerator:
        def answer(self, question, retrieved):
            return GeneratedAnswer(
                "Attention answer [1]",
                [SourceCitation(1, "Book", 4, 4, "chunk-1")],
                True,
                0.9,
            )

    service = RAGService(indexer=None, retriever=FakeRetriever(), generator=FakeGenerator())
    result = service.query("What is attention?", k=3, book_title="Book")

    assert result.generated.answer == "Attention answer [1]"
    assert result.retrieved[0].chunk.chunk_id == "chunk-1"
