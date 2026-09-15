# Phase 6 Overview

Phase 6 adds an evaluation harness for measuring retrieval and grounded-answer behavior. Cases are stored as JSONL so the dataset can grow to the requested 20-30 questions without changing application code.

## Metrics

- `retrieval_recall_at_k`: percentage of questions where at least one expected relevant chunk appears in the top-k results.
- `retrieval_hit_rate_at_k`: currently the same binary metric for this single-hit-per-question dataset; it is kept as a separate name for future multi-relevant-document metrics.
- `mean_faithfulness`: average lexical support score between the answer and retrieved context.
- `faithfulness_pass_rate`: percentage whose support score clears the configured threshold and whose generator marked the answer grounded.
- `citation_valid_rate`: percentage whose returned citation chunk IDs came from the retrieved set.

## Running With Real Data

Copy `eval/questions.example.jsonl` to a working evaluation file, replace the placeholders with real questions, expected answers, and relevant chunk IDs from your indexed books, then run the harness from Python with your configured `Retriever` and `GroundedGenerator`. Use `write_report(...)` to save a JSON report for before/after comparisons.

The expected chunk IDs make retrieval recall objective. They can be captured from the indexed Chroma collection or from a manually reviewed retrieval run. Build 20-30 cases across books, chapters, easy questions, multi-hop questions, and questions whose answer is absent from the library.

## Honest Simplification

Lexical support is a transparent diagnostic, not a true semantic faithfulness or entailment judge. It can penalize valid paraphrases and reward copied but misleading words. A production evaluation would add human labels, an entailment model or carefully controlled LLM judge, and separate answer-correctness scoring against the expected answer.
