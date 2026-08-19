import json
from pathlib import Path

from src.models.schemas import ComplianceRequest
from src.retrieval.retriever import PolicyRetriever
from src.retrieval.reranker import JinaReranker
from src.analysis.compliance_judge import ComplianceJudge
from src.retrieval.query_builder import build_retrieval_query

class PolicyLensEvaluator:
    def __init__(self):
        self.retriever = PolicyRetriever()
        self.reranker = JinaReranker()
        self.judge = ComplianceJudge()

    def load_test_cases(self, directory: str):

        test_cases = []

        directory_path = Path(directory)

        for file_path in directory_path.glob("*.json"):

            with open(file_path, "r", encoding="utf-8") as file:
                cases = json.load(file)

            for case in cases:
                case["policy_file"] = file_path.stem

            test_cases.extend(cases)

        return test_cases

    def evaluate_case(self, test_case: dict):

        request = ComplianceRequest(
            employee=test_case["employee"],
            department=test_case["department"],
            request=test_case["request"],
            reason  = test_case["reason"],
        )

        retrieval_query = build_retrieval_query(request)

        retrieved_chunks = self.retriever.retrieve(retrieval_query)

        reranked_chunks = self.reranker.rerank(
            query=retrieval_query,
            chunks = retrieved_chunks,
            top_n=8,
        )

        judgement = self.judge.analyze(
            request=request,
            evidence=reranked_chunks,
        )

        actual_verdict = judgement.verdict.value
        expected_verdict = test_case["expected_verdict"]

        passed = actual_verdict == expected_verdict

        return {
            "case_id": test_case["case_id"],
            "expected_verdict": expected_verdict,
            "actual_verdict": actual_verdict,
            "passed": passed,
            "relevance": judgement.relevance.model_dump(),
            "requirements": [
                requirement.model_dump()
                for requirement in judgement.requirements
            ],
            "violations": judgement.violations,
            "missing_evidence": judgement.missing_evidence,
            "explanation": judgement.explanation,
            "retrieved_chunks": [
                chunk.model_dump()
                for chunk in retrieved_chunks
            ],
            "reranked_chunks": [
                chunk.model_dump()
                for chunk in reranked_chunks
            ],
        }


        