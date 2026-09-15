from __future__ import annotations

import httpx

from app.chunking.metadata import make_chunk
from app.core.models import ExtractedPage, ParsedDocument, SourceDocument
from app.embeddings.ollama_client import OllamaEmbedder
from app.index.indexer import ChunkIndexer


def _chunks(count: int = 3):
    document = ParsedDocument(
        document=SourceDocument(document_id="book-1", source_path="book.pdf", title="Book"),
        pages=[ExtractedPage(page_number=1, text="text")],
    )
    return [
        make_chunk(
            document,
            chunk_index=index,
            text=f"chunk {index}",
            page_start=1,
            page_end=1,
        )
        for index in range(count)
    ]


def test_ollama_embedder_posts_batch_and_returns_vectors():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/embed"
        assert request.read()
        return httpx.Response(200, json={"embeddings": [[0.1, 0.2], [0.3, 0.4]]})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    embedder = OllamaEmbedder("http://ollama:11434", "nomic-embed-text", client=client)

    assert embedder.embed(["one", "two"]) == [[0.1, 0.2], [0.3, 0.4]]
    client.close()


def test_indexer_batches_embeddings_and_upserts_incrementally():
    class FakeEmbedder:
        def __init__(self):
            self.calls = []

        def embed(self, texts):
            self.calls.append(list(texts))
            return [[float(index)] for index, _ in enumerate(texts)]

    class FakeStore:
        def __init__(self):
            self.upserts = []

        def upsert_chunks(self, chunks, embeddings):
            self.upserts.append((chunks, embeddings))

    embedder = FakeEmbedder()
    store = FakeStore()
    indexed = ChunkIndexer(embedder, store, batch_size=2).index(_chunks())

    assert indexed == 3
    assert len(embedder.calls) == 2
    assert [len(batch[0]) for batch in store.upserts] == [2, 1]
