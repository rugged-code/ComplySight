from src.models.schemas import ComplianceRequest
from src.retrieval.retriever import PolicyRetriever
from src.retrieval.reranker import JinaReranker
from src.analysis.compliance_judge import ComplianceJudge


request = ComplianceRequest(
    employee="Jessica Lin",
    department="Facilities",
    request=(
        "Please generate a purchase order for our new office cleaning "
        "vendor, CleanCo. The total annualized contract value is $20,000. "
        "I have attached the signed contract and they will start on the "
        "1st of next month."
    ),
    reason="To hire a new cleaning service for the main office.",
)





retriever = PolicyRetriever(top_k=20)

retrieved_chunks = retriever.retrieve(request.request)

print(f"Retrieved: {len(retrieved_chunks)}")







reranker = JinaReranker()

reranked_chunks = reranker.rerank(
    query=request.request,
    chunks=retrieved_chunks,
    top_n=5,
)

print(f"Reranked: {len(reranked_chunks)}")






judge = ComplianceJudge()

judgment = judge.analyze(
    request=request,
    evidence=reranked_chunks,
)







print("\n")
print("=" * 60)
print("COMPLIANCE JUDGMENT")
print("=" * 60)

print("\nVerdict:")
print(judgment.verdict.value)


print("\nRequirements:")

for requirement in judgment.requirements:
    print(f"- {requirement.description}")
    print(f"  Section: {requirement.section}")
    print(f"  Satisfied: {requirement.satisfied}")


print("\nViolations:")

for violation in judgment.violations:
    print(f"- {violation}")


print("\nMissing Evidence:")

for missing in judgment.missing_evidence:
    print(f"- {missing}")


print("\nEvidence:")

for evidence in judgment.evidence:
    print(f"- {evidence.policy} §{evidence.section}")
    print(f"  Source: {evidence.source}")
    print(f"  Content: {evidence.content}")


print("\nExplanation:")
print(judgment.explanation)