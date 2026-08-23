# RAG App

Local retrieval-augmented generation app for AI/ML books, built with Python, Ollama, and ChromaDB.

## Status

Phase 0 scaffold only:
- project layout
- shared config and domain models
- FastAPI health endpoint
- Docker Compose and environment template

See [docs/phase0_overview.md](docs/phase0_overview.md) for the folder-by-folder explanation and data flow diagram.

Phase 1 started:
- PDF and EPUB ingestion modules
- text cleaning and normalization
- document parser entrypoint

See [docs/phase1_overview.md](docs/phase1_overview.md) for the ingestion flow and simplifications.

## Next steps

1. Document ingestion
2. Chunking
3. Embeddings and indexing
4. Retrieval and reranking
5. Grounded generation
6. Evaluation
7. UI
