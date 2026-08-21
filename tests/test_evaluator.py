import itertools
import json
import time
from pathlib import Path

import requests

from src.models.schemas import ComplianceRequest
from src.retrieval.retriever import PolicyRetriever
from src.retrieval.reranker import JinaReranker
from src.retrieval.query_builder import build_retrieval_query
from src.analysis.compliance_judge import ComplianceJudge


TEST_CASE_DIR = Path("data/evaluation")
OUTPUT_FILE = "evaluation_results.json"

BATCH_SIZE = 10
BATCH_DELAY = 30    # seconds between batches
LLM_DELAY = 5       # seconds between Gemini calls (~12 rpm; limit is 15)

MAX_RETRIES = 3
RETRY_DELAY = 5      # seconds, multiplied by attempt number


def load_test_cases():
    cases = []
    for file_path in sorted(TEST_CASE_DIR.glob("*.json")):
        data = json.loads(file_path.read_text(encoding="utf-8"))
        cases.extend(data if isinstance(data, list) else [data])
    return cases


def with_retry(fn, *, retryable=lambda e: True, label="call"):
    """Call fn() with retries. `retryable(exc)` decides if an error is worth retrying."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return fn()
        except Exception as e:
            if not retryable(e) or attempt == MAX_RETRIES:
                raise
            wait = RETRY_DELAY * attempt
            print(f"{label} failed (attempt {attempt}/{MAX_RETRIES}): {e} -- retrying in {wait}s")
            time.sleep(wait)


def is_server_error(e):
    """Only a 5xx is worth retrying -- a 4xx or a malformed response won't fix itself."""
    return (
        isinstance(e, requests.exceptions.HTTPError)
        and e.response is not None
        and e.response.status_code >= 500
    )


def batched(seq, size):
    it = iter(seq)
    while chunk := list(itertools.islice(it, size)):
        yield chunk


def run_case(case, retriever, reranker, judge):
    case_id = case["case_id"]
    expected = case["expected_verdict"]
    print(f"\n{'-' * 60}\n{case_id} | expected: {expected}")

    request = ComplianceRequest(
        employee=case["employee"],
        department=case["department"],
        request=case["request"],
        reason=case["reason"],
        additional_information=case.get("additional_information", ""),
    )
    query = build_retrieval_query(request)

    try:
        retrieved = with_retry(lambda: retriever.retrieve(query), label="Qdrant retrieval")
        print(f"Retrieved: {len(retrieved)}")
    except Exception as e:
        print(f"RETRIEVAL ERROR: {e}")
        return {
            "case_id": case_id, "expected": expected, "actual": None,
            "passed": False, "status": "RETRIEVAL_ERROR", "error": str(e),
        }

    try:
        reranked = with_retry(
            lambda: reranker.rerank(query=query, chunks=retrieved, top_n=8),
            retryable=is_server_error,
            label="Jina rerank",
        )
        print(f"Reranked: {len(reranked)}")
    except Exception as e:
        print(f"RERANKING ERROR: {e}")
        return {
            "case_id": case_id, "expected": expected, "actual": None,
            "passed": False, "status": "RERANKING_ERROR", "error": str(e),
            "retrieved_sections": [
                {"document": c.document, "section": c.section} for c in retrieved
            ],
        }

    try:
        judgment = judge.analyze(
            request=request,
            evidence=reranked,
            query=query,
            reranker=reranker,
        )
        actual = judgment.verdict.value
    except Exception as e:
        print(f"JUDGE ERROR: {e}")
        return {
            "case_id": case_id, "expected": expected, "actual": None,
            "passed": False, "status": "JUDGE_ERROR", "error": str(e),
        }

    passed_case = actual == expected
    print(f"Actual: {actual} | Passed: {passed_case}")

    return {
        "case_id": case_id,
        "expected": expected,
        "actual": actual,
        "passed": passed_case,
        "status": "COMPLETED",
        "retrieved_sections": [
            {
                "document": chunk.document,
                "section": chunk.section,
                "qdrant_score": chunk.qdrant_score,
            }
            for chunk in retrieved
        ],
        "reranked_sections": [
            {
                "document": chunk.document,
                "section": chunk.section,
                "qdrant_score": chunk.qdrant_score,
                "rerank_score": chunk.rerank_score,
            }
            for chunk in reranked
        ],
        "relevance": judgment.relevance.model_dump(),
        "requirements": [
            requirement.model_dump()
            for requirement in judgment.requirements
        ],
        "violations": judgment.violations,
        "missing_evidence": judgment.missing_evidence,
        "evidence": [
            evidence_item.model_dump()
            for evidence_item in judgment.evidence
        ],
        "explanation": judgment.explanation,
    }


def main():
    cases = load_test_cases()
    print(f"Total test cases: {len(cases)}")

    retriever = PolicyRetriever(top_k=30)
    reranker = JinaReranker()
    judge = ComplianceJudge()

    batches = list(batched(cases, BATCH_SIZE))
    results = []

    for batch_num, batch in enumerate(batches, start=1):
        print(f"\n{'=' * 70}\nBATCH {batch_num}/{len(batches)} ({len(batch)} cases)\n{'=' * 70}")

        for i, case in enumerate(batch):
            results.append(run_case(case, retriever, reranker, judge))
            if i < len(batch) - 1:
                time.sleep(LLM_DELAY)

        if batch_num < len(batches):
            print(f"\nBatch {batch_num} complete. Waiting {BATCH_DELAY}s before next batch...")
            time.sleep(BATCH_DELAY)

    completed = [r for r in results if r["status"] == "COMPLETED"]
    passed = sum(r["passed"] for r in completed)
    errors = {
        status: sum(1 for r in results if r["status"] == status)
        for status in ("RETRIEVAL_ERROR", "RERANKING_ERROR", "JUDGE_ERROR")
    }

    print(f"\n{'=' * 70}\nFINAL EVALUATION\n{'=' * 70}")
    print(f"Total cases:       {len(cases)}")
    print(f"Completed:         {len(completed)}")
    print(f"Passed:            {passed}")
    print(f"Failed:            {len(completed) - passed}")
    for status, count in errors.items():
        print(f"{status}:  {count}")
    if completed:
        print(f"Accuracy (of completed only): {passed / len(completed):.2%}")
    print(f"Accuracy (of all {len(cases)} cases, errors counted as fails): "
          f"{passed / len(cases):.2%}" if cases else "N/A")

    Path(OUTPUT_FILE).write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nResults saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()