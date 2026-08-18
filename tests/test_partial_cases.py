import json
import time

from src.models.schemas import ComplianceRequest
from src.retrieval.retriever import PolicyRetriever
from src.retrieval.reranker import JinaReranker
from src.retrieval.query_builder import build_retrieval_query
from src.analysis.compliance_judge import ComplianceJudge


PARTIAL_CASES = {
    "AC-003",
    "DP-003",
    "DU-003",
    "EC-003",
    "EXP-003",
    "IR-003",
    "SEC-003",
    "AUTH-003",
    "RW-003",
    "VND-003",
}


def load_partial_cases():

    cases = []

    for file_path in sorted(
        __import__("pathlib").Path("data/evaluation").glob("*.json")
    ):

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            cases.extend(data)
        else:
            cases.append(data)

    return [
        case
        for case in cases
        if case["case_id"] in PARTIAL_CASES
    ]


def main():

    cases = load_partial_cases()

    print(f"Total partial cases: {len(cases)}")

    retriever = PolicyRetriever(top_k=20)
    reranker = JinaReranker()
    judge = ComplianceJudge()

    passed = 0
    failed = 0

    for i, case in enumerate(cases):

        print("\n" + "=" * 70)
        print(f"Testing: {case['case_id']}")
        print(f"Expected: {case['expected_verdict']}")

        request = ComplianceRequest(
            employee=case["employee"],
            department=case["department"],
            request=case["request"],
            reason=case["reason"],
            additional_information=case.get(
                "additional_information",
                ""
            )
        )

        # 1. Build retrieval query
        query = build_retrieval_query(request)

        # 2. Qdrant retrieval
        retrieved = retriever.retrieve(query)

        print(f"Retrieved: {len(retrieved)}")

        print("\nRetrieved sections:")

        for chunk in retrieved:
            print(
                f"  {chunk.document} | "
                f"Section: {chunk.section}"
            )

        # 3. Reranking
        reranked = reranker.rerank(
            query=query,
            chunks=retrieved,
            top_n=5
        )

        print(f"\nReranked: {len(reranked)}")

        print("\nReranked sections:")

        for chunk in reranked:
            print(
                f"  {chunk.document} | "
                f"Section: {chunk.section} | "
                f"Score: {chunk.rerank_score}"
            )

        # 4. Gemini judgment
        judgment = judge.analyze(
            request=request,
            evidence=reranked
        )

        actual = judgment.verdict.value
        expected = case["expected_verdict"]

        passed_case = actual == expected

        if passed_case:
            passed += 1
        else:
            failed += 1

        print("\n" + "-" * 70)
        print(f"Expected: {expected}")
        print(f"Actual:   {actual}")
        print(f"Passed:   {passed_case}")

        # Show requirement-level result
        print("\nRequirements:")

        for requirement in judgment.requirements:

            if hasattr(requirement, "status"):
                status = requirement.status.value
            elif hasattr(requirement, "satified"):
                status = requirement.satified
            else:
                status = "N/A"

            print(
                f"  Section {requirement.section}: "
                f"{status}"
            )

            print(
                f"    {requirement.description}"
            )

        print("\nExplanation:")
        print(judgment.explanation)

        # Wait before next Gemini call
        if i < len(cases) - 1:
            print("\nWaiting 6 seconds...")
            time.sleep(6)

    print("\n" + "=" * 70)
    print("PARTIAL COMPLIANCE RESULTS")
    print("=" * 70)

    print(f"Total:  {len(cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if cases:
        print(
            f"Accuracy: "
            f"{passed / len(cases):.2%}"
        )


if __name__ == "__main__":
    main()