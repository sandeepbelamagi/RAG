# RAG App

Local retrieval-augmented generation app for AI/ML books, built with Python, Ollama, and ChromaDB.

## Status

Phases 0-5 are implemented:
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

Phase 3 started:
- Ollama batch embedding client
- persistent ChromaDB vector store
- incremental batch indexing with stable chunk IDs

See [docs/phase3_overview.md](docs/phase3_overview.md) for the embedding and indexing flow.

Phase 4 started:
- top-k vector retrieval
- Chroma metadata filtering
- MMR diversity reranking

See [docs/phase4_overview.md](docs/phase4_overview.md) for the retrieval flow and trade-offs.

Phase 5 started:
- grounded Ollama generation
- explicit context injection and citation markers
- low-confidence “I don't know” fallback

See [docs/phase5_overview.md](docs/phase5_overview.md) for the generation flow and prompt contract.

## Next steps

1. Evaluation and metrics
2. FastAPI query and ingestion integration
3. Streamlit or React UI
