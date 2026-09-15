from app.core.models import DocumentChunk, RetrievedChunk
from app.generation.generator import GroundedGenerator, UNKNOWN_ANSWER
from app.generation.prompt import build_user_prompt


def _retrieved(score: float = 0.8) -> list[RetrievedChunk]:
    return [
        RetrievedChunk(
            chunk=DocumentChunk(
                chunk_id="chunk-1",
                document_id="book-1",
                text="Attention allows tokens to weigh information from other tokens.",
                page_start=42,
                metadata={"book_title": "Transformer Book"},
            ),
            score=score,
            rank=1,
        )
    ]


def test_prompt_contains_context_question_and_citation_marker():
    prompt = build_user_prompt("What is attention?", _retrieved())

    assert "Transformer Book, page 42" in prompt
    assert "Attention allows" in prompt
    assert "What is attention?" in prompt
    assert "[1]" in prompt


def test_generator_injects_context_and_returns_citation():
    class FakeChat:
        def __init__(self):
            self.user_prompt = ""

        def chat(self, *, system, user):
            assert "only from the supplied CONTEXT" in system
            self.user_prompt = user
            return "Attention lets tokens use information from other tokens. [1]"

    chat = FakeChat()
    result = GroundedGenerator(chat).answer("What is attention?", _retrieved())

    assert result.grounded is True
    assert result.citations[0].page_start == 42
    assert "Attention allows" in chat.user_prompt


def test_generator_returns_unknown_when_retrieval_confidence_is_low():
    class FailingChat:
        def chat(self, **kwargs):
            raise AssertionError("the LLM must not be called for low confidence")

    result = GroundedGenerator(FailingChat(), min_retrieval_score=0.5).answer(
        "What is attention?",
        _retrieved(score=0.2),
    )

    assert result.answer == UNKNOWN_ANSWER
    assert result.grounded is False
    assert result.citations == []
