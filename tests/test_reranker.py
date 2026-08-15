from src.retrieval.retriever import PolicyRetriever
from src.retrieval.reranker import JinaReranker


query = """
I want to finalize a $60,000 contract with a new vendor
that will process Confidential analytics data.
The Vendor Risk Assessment is complete,
the Information Security Addendum is signed,
and I have approval from the Head of Procurement
and CFO.
"""


retriever = PolicyRetriever(top_k=20)

results = retriever.retrieve(query)

print(f"Retrieved: {len(results)}")



reranker = JinaReranker()

reranked_results = reranker.rerank(
    query=query,
    results=results,
    top_n=5
)



print("\nRERANKED RESULTS")
print("=" * 60)

for rank, result in enumerate(reranked_results, start=1):

    payload = result["payload"]

    print(f"\nRank: {rank}")

    print("Qdrant score:", result["qdrant_score"])
    print("Rerank score:", result["rerank_score"])

    print("Policy:", payload.get("document"))
    print("Section:", payload.get("section"))
    print("Title:", payload.get("section_title"))
    print("Source:", payload.get("source"))

    print("\nText:")
    print(payload.get("text"))