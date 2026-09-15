from app.core.models import DocumentChunk, RetrievedChunk
from app.eval.harness import EvalCase, EvaluationHarness, lexical_support_score
from app.generation.generator import GeneratedAnswer, SourceCitation


def _retrieved(chunk_id: str = "chunk-1") -> list[RetrievedChunk]:
    return [
        RetrievedChunk(
            chunk=DocumentChunk(
                chunk_id=chunk_id,
                document_id="book-1",
                text="Attention uses weighted combinations of token representations.",
            ),
            score=0.8,
            rank=1,
        )
    ]


def test_lexical_support_score_is_explainable():
    score = lexical_support_score(
        "Attention uses weighted token representations.",
        "Attention uses weighted combinations of token representations.",
    )

    assert score == 1.0


def test_harness_calculates_recall_and_faithfulness():
    class FakeRetriever:
        def retrieve(self, query, *, k, where):
            assert k == 2
            return _retrieved()

    class FakeGenerator:
        def answer(self, question, retrieved):
            return GeneratedAnswer(
                answer="Attention uses weighted token representations. [1]",
                citations=[SourceCitation(1, "Book", None, None, "chunk-1")],
                grounded=True,
                confidence=0.8,
            )

    summary = EvaluationHarness(FakeRetriever(), FakeGenerator()).evaluate(
        [EvalCase("q1", "What is attention?", "Weighted combinations", ["chunk-1"])],
        k=2,
    )

    assert summary.retrieval_recall_at_k == 1.0
    assert summary.retrieval_hit_rate_at_k == 1.0
    assert summary.faithfulness_pass_rate == 1.0
    assert summary.citation_valid_rate == 1.0


def test_harness_marks_missing_relevant_chunk_as_retrieval_miss():
    class FakeRetriever:
        def retrieve(self, query, *, k, where):
            return _retrieved()

    class FakeGenerator:
        def answer(self, question, retrieved):
            return GeneratedAnswer("I don't know", [], False, 0.1)

    summary = EvaluationHarness(FakeRetriever(), FakeGenerator()).evaluate(
        [EvalCase("q1", "Question", "Expected", ["different-chunk"])],
    )

    assert summary.retrieval_recall_at_k == 0.0
    assert summary.faithfulness_pass_rate == 0.0
