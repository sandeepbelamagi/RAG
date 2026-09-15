from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.core.models import RetrievedChunk
from app.generation.prompt import SYSTEM_PROMPT, build_user_prompt


UNKNOWN_ANSWER = "I don't know based on the provided book context."


class ChatModel(Protocol):
    def chat(self, *, system: str, user: str) -> str: ...


@dataclass(slots=True)
class SourceCitation:
    marker: int
    title: str
    page_start: int | None
    page_end: int | None
    chunk_id: str


@dataclass(slots=True)
class GeneratedAnswer:
    answer: str
    citations: list[SourceCitation]
    grounded: bool
    confidence: float


class GroundedGenerator:
    def __init__(
        self,
        chat_model: ChatModel,
        *,
        min_retrieval_score: float = 0.35,
        system_prompt: str = SYSTEM_PROMPT,
    ) -> None:
        if not 0 <= min_retrieval_score <= 1:
            raise ValueError("min_retrieval_score must be between 0 and 1")
        self.chat_model = chat_model
        self.min_retrieval_score = min_retrieval_score
        self.system_prompt = system_prompt

    def answer(self, question: str, retrieved: list[RetrievedChunk]) -> GeneratedAnswer:
        if not question.strip():
            raise ValueError("question must not be empty")
        confidence = max((item.score for item in retrieved), default=0.0)
        if not retrieved or confidence < self.min_retrieval_score:
            return GeneratedAnswer(UNKNOWN_ANSWER, [], False, confidence)

        response = self.chat_model.chat(
            system=self.system_prompt,
            user=build_user_prompt(question, retrieved),
        )
        return GeneratedAnswer(
            answer=response,
            citations=_citations(retrieved),
            grounded=True,
            confidence=confidence,
        )


def _citations(retrieved: list[RetrievedChunk]) -> list[SourceCitation]:
    citations = []
    for marker, item in enumerate(retrieved, start=1):
        metadata = item.chunk.metadata
        citations.append(
            SourceCitation(
                marker=marker,
                title=str(metadata.get("book_title") or metadata.get("source_path") or "Unknown source"),
                page_start=item.chunk.page_start,
                page_end=item.chunk.page_end,
                chunk_id=item.chunk.chunk_id,
            )
        )
    return citations
