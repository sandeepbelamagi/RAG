from app.core.models import DocumentChunk
from app.index.chroma_store import VectorMatch
from app.retrieval.retriever import Retriever, mmr_rerank


def _match(chunk_id: str, embedding: list[float], title: str = "Book") -> VectorMatch:
    return VectorMatch(
        chunk=DocumentChunk(
            chunk_id=chunk_id,
            document_id="doc-1",
            text=chunk_id,
            metadata={"book_title": title},
        ),
        distance=0.1,
        embedding=embedding,
    )


def test_mmr_returns_relevant_and_diverse_chunks():
    matches = [
        _match("same-a", [1.0, 0.0]),
        _match("same-b", [0.99, 0.01]),
        _match("different", [0.0, 1.0]),
    ]

    results = mmr_rerank([1.0, 0.0], matches, limit=2, diversity=0.6)

    assert [result.chunk.chunk_id for result in results] == ["same-a", "different"]
    assert [result.rank for result in results] == [1, 2]


def test_retriever_embeds_query_and_passes_metadata_filter():
    class FakeEmbedder:
        def embed_one(self, query):
            assert query == "What is attention?"
            return [1.0, 0.0]

    class FakeStore:
        def search(self, query_embedding, *, limit, where):
            assert query_embedding == [1.0, 0.0]
            assert limit == 6
            assert where == {"book_title": "Book"}
            return [_match("chunk-1", [1.0, 0.0])]

    results = Retriever(FakeEmbedder(), FakeStore(), candidate_multiplier=2).retrieve(
        "What is attention?",
        k=3,
        where={"book_title": "Book"},
    )

    assert len(results) == 1
    assert results[0].chunk.chunk_id == "chunk-1"
