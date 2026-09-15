# RAG App

Local retrieval-augmented generation app for AI/ML books, built with Python, Ollama, and ChromaDB.

## Status

Phases 0-9 are implemented:
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

Phase 6 started:
- JSONL evaluation case format
- retrieval recall/hit-rate metrics
- heuristic faithfulness and citation-validity metrics
- JSON metrics report support

See [docs/phase6_overview.md](docs/phase6_overview.md) for the evaluation methodology and limitations.

Phase 7 started:
- FastAPI `/ingest` endpoint for PDF and EPUB uploads
- FastAPI `/query` endpoint with book filtering
- answer, citations, confidence, and source chunks in the response

See [docs/phase7_overview.md](docs/phase7_overview.md) for the API flow and production limitations.

Phase 8 started:
- Streamlit chat interface
- PDF/EPUB upload controls
- answer confidence, citations, and retrieved source display

See [docs/phase8_overview.md](docs/phase8_overview.md) for UI setup and trade-offs.

Phase 9 started:
- request logging with request IDs and durations
- `/ready` dependency readiness endpoint
- upload-size protection, Docker health checks, and CI workflow

See [docs/phase9_overview.md](docs/phase9_overview.md) for hardening scope and limitations.

## Next steps

1. Deployment-specific configuration and operational runbooks
