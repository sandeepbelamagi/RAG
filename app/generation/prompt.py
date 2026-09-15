from __future__ import annotations

from app.core.models import RetrievedChunk


SYSTEM_PROMPT = """You are a careful assistant answering questions about a private book library.
Answer only from the supplied CONTEXT. Do not use outside knowledge or invent missing details.
If the context does not support an answer, say exactly that the information is not available in
the provided books. Cite every factual claim with one or more context markers such as [1] or [2].
Keep the answer concise and explain uncertainty when the sources disagree."""


def _source_label(retrieved: RetrievedChunk) -> str:
    metadata = retrieved.chunk.metadata
    title = metadata.get("book_title") or metadata.get("source_path") or "Unknown source"
    page_start = retrieved.chunk.page_start
    page_end = retrieved.chunk.page_end
    if page_start is None:
        location = "page unavailable"
    elif page_end and page_end != page_start:
        location = f"pages {page_start}-{page_end}"
    else:
        location = f"page {page_start}"
    return f"{title}, {location}"


def build_context(chunks: list[RetrievedChunk]) -> str:
    """Format retrieved chunks with stable citation markers for the LLM."""
    sections = []
    for index, retrieved in enumerate(chunks, start=1):
        sections.append(
            f"[{index}] SOURCE: {_source_label(retrieved)}\n"
            f"TEXT:\n{retrieved.chunk.text.strip()}"
        )
    return "\n\n".join(sections)


def build_user_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        raise ValueError("At least one retrieved chunk is required")
    return (
        "CONTEXT:\n"
        f"{build_context(chunks)}\n\n"
        "QUESTION:\n"
        f"{question.strip()}\n\n"
        "Write a grounded answer with citations in the format [number]."
    )
