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

chunks = retriever.retrieve(query)

print(f"Retrieved: {len(chunks)}")


reranker = JinaReranker()

reranked_chunks = reranker.rerank(
    query=query,
    chunks=chunks,
    top_n=5
)


print("\nRERANKED RESULTS")
print("=" * 60)


for rank, chunk in enumerate(reranked_chunks, start=1):

    print(f"\nRank: {rank}")

    print("Qdrant score:", chunk.qdrant_score)
    print("Rerank score:", chunk.rerank_score)

    print("Policy:", chunk.document)
    print("Section:", chunk.section)
    print("Title:", chunk.section_title)
    print("Source:", chunk.source)

    print("\nText:")
    print(chunk.text)