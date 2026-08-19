import json
import time
from pathlib import Path

from src.models.schemas import ComplianceRequest
from src.retrieval.retriever import PolicyRetriever
from src.retrieval.reranker import JinaReranker
from src.retrieval.query_builder import build_retrieval_query
from src.analysis.compliance_judge import ComplianceJudge


FAILED_CASES = {
    # NON_COMPLIANT that became PARTIAL
    "AC-002",
    "DP-002",
    "EXP-002",
    "AUTH-002",
    "RW-002",
    "VND-002",

    # PARTIAL that became COMPLIANT
    "AUTH-003",
}


def load_failed_cases():
    cases = []
    for file_path in sorted(Path("data/evaluation").glob("*.json")):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            cases.extend(data)
        else:
            cases.append(data)

    return [c for c in cases if c["case_id"] in FAILED_CASES]


def main():
    cases = load_failed_cases()
    print(f"Running {len(cases)} previously failed cases\n")

    retriever = PolicyRetriever(top_k=30)
    reranker = JinaReranker()
    judge = ComplianceJudge()

    passed = 0
    failed = 0
    results = []

    for i, case in enumerate(cases):
        case_id = case["case_id"]
        expected = case["expected_verdict"]

        request = ComplianceRequest(
            employee=case["employee"],
            department=case["department"],
            request=case["request"],
            reason=case["reason"],
            additional_information=case.get("additional_information", ""),
        )

        query = build_retrieval_query(request)
        retrieved = retriever.retrieve(query)
        reranked = reranker.rerank(query=query, chunks=retrieved, top_n=8)
        judgment = judge.analyze(request=request, evidence=reranked)

        actual = judgment.verdict.value
        ok = actual == expected

        if ok:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        print(f"{case_id:12} | Expected: {expected:22} | Actual: {actual:22} | {status}")

        results.append({
            "case_id": case_id,
            "expected": expected,
            "actual": actual,
            "passed": ok,
        })

        if i < len(cases) - 1:
            time.sleep(4)

    print("\n" + "=" * 60)
    print(f"Total: {len(cases)}  |  Passed: {passed}  |  Failed: {failed}")
    print(f"Accuracy: {passed / len(cases):.1%}")
    print("=" * 60)

    print("\nStill failing:")
    for r in results:
        if not r["passed"]:
            print(f"  {r['case_id']}: {r['expected']} -> {r['actual']}")


if __name__ == "__main__":
    main()