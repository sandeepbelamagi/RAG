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

Configured storage locations:
- PDFs/EPUBs: `/Users/macbook/Documents/GenAI/Projects/Data/pdf_data`
- ChromaDB: `/Users/macbook/Documents/GenAI/Projects/Data/DBs/chroma`

Phase 2 started:
- fixed-size chunking with overlap
- structure-aware chunking by headings
- chunk metadata and stable chunk IDs

See [docs/phase2_overview.md](docs/phase2_overview.md) for the chunking flow and trade-offs.

## Next steps

1. Document ingestion
2. Chunking
3. Embeddings and indexing
4. Retrieval and reranking
5. Grounded generation
6. Evaluation
7. UI
