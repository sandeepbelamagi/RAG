from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol

from app.core.models import RetrievedChunk
from app.generation.generator import GeneratedAnswer


class EvalRetriever(Protocol):
    def retrieve(
        self,
        query: str,
        *,
        k: int,
        where: dict[str, Any] | None = None,
    ) -> list[RetrievedChunk]: ...


class EvalGenerator(Protocol):
    def answer(self, question: str, retrieved: list[RetrievedChunk]) -> GeneratedAnswer: ...


@dataclass(slots=True)
class EvalCase:
    case_id: str
    question: str
    expected_answer: str
    relevant_chunk_ids: list[str]
    metadata_filter: dict[str, Any] | None = None


@dataclass(slots=True)
class CaseResult:
    case_id: str
    question: str
    retrieved_chunk_ids: list[str]
    retrieval_hit: bool
    answer: str
    faithfulness_score: float
    faithfulness_passed: bool
    citation_valid: bool


@dataclass(slots=True)
class EvaluationSummary:
    k: int
    case_count: int
    retrieval_recall_at_k: float
    retrieval_hit_rate_at_k: float
    mean_faithfulness: float
    faithfulness_pass_rate: float
    citation_valid_rate: float
    results: list[CaseResult]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EvaluationHarness:
    def __init__(
        self,
        retriever: EvalRetriever,
        generator: EvalGenerator,
        *,
        faithfulness_threshold: float = 0.6,
    ) -> None:
        if not 0 <= faithfulness_threshold <= 1:
            raise ValueError("faithfulness_threshold must be between 0 and 1")
        self.retriever = retriever
        self.generator = generator
        self.faithfulness_threshold = faithfulness_threshold

    def evaluate(self, cases: list[EvalCase], *, k: int = 5) -> EvaluationSummary:
        if k <= 0:
            raise ValueError("k must be positive")
        if not cases:
            raise ValueError("at least one evaluation case is required")

        results = [self._evaluate_case(case, k=k) for case in cases]
        case_count = len(results)
        return EvaluationSummary(
            k=k,
            case_count=case_count,
            retrieval_recall_at_k=sum(result.retrieval_hit for result in results) / case_count,
            retrieval_hit_rate_at_k=sum(result.retrieval_hit for result in results) / case_count,
            mean_faithfulness=sum(result.faithfulness_score for result in results) / case_count,
            faithfulness_pass_rate=sum(result.faithfulness_passed for result in results) / case_count,
            citation_valid_rate=sum(result.citation_valid for result in results) / case_count,
            results=results,
        )

    def _evaluate_case(self, case: EvalCase, *, k: int) -> CaseResult:
        retrieved = self.retriever.retrieve(
            case.question,
            k=k,
            where=case.metadata_filter,
        )
        retrieved_ids = [item.chunk.chunk_id for item in retrieved]
        retrieval_hit = bool(set(retrieved_ids) & set(case.relevant_chunk_ids))
        generated = self.generator.answer(case.question, retrieved)
        context = " ".join(item.chunk.text for item in retrieved)
        faithfulness = lexical_support_score(generated.answer, context)
        cited_ids = {citation.chunk_id for citation in generated.citations}
        citation_valid = cited_ids.issubset(set(retrieved_ids))
        return CaseResult(
            case_id=case.case_id,
            question=case.question,
            retrieved_chunk_ids=retrieved_ids,
            retrieval_hit=retrieval_hit,
            answer=generated.answer,
            faithfulness_score=faithfulness,
            faithfulness_passed=faithfulness >= self.faithfulness_threshold and generated.grounded,
            citation_valid=citation_valid,
        )


def lexical_support_score(answer: str, context: str) -> float:
    """Return the fraction of meaningful answer terms present in retrieved context.

    This is a diagnostic heuristic, not a semantic entailment metric. It is intentionally
    simple so evaluation results remain explainable without another model or API call.
    """
    answer_terms = _meaningful_terms(answer)
    context_terms = _meaningful_terms(context)
    if not answer_terms:
        return 0.0
    return len(answer_terms & context_terms) / len(answer_terms)


def load_cases(path: str | Path) -> list[EvalCase]:
    cases = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            payload = json.loads(line)
            cases.append(EvalCase(**payload))
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError(f"Invalid evaluation case on line {line_number}") from exc
    return cases


def write_report(summary: EvaluationSummary, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary.to_dict(), indent=2) + "\n", encoding="utf-8")


_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "in",
    "is", "it", "of", "on", "or", "that", "the", "their", "this", "to", "was", "what",
    "when", "where", "which", "with", "you", "your",
}


def _meaningful_terms(text: str) -> set[str]:
    terms = set(re.findall(r"[a-zA-Z][a-zA-Z0-9-]{2,}", text.lower()))
    return terms - _STOP_WORDS
