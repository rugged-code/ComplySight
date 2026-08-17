from src.retrieval.retriever import PolicyRetriever
from src.retrieval.bge_reranker import BGEReranker


query = """
YOUR AC-001 REQUEST HERE
"""


retriever = PolicyRetriever(top_k=20)

chunks = retriever.retrieve(query)

print(f"Retrieved: {len(chunks)}")


reranker = BGEReranker()

results = reranker.rerank(
    query=query,
    chunks=chunks,
    top_n=5
)


print("\nBGE RERANKED RESULTS")
print("=" * 60)

for i, result in enumerate(results, start=1):

    print(f"\nRank: {i}")
    print(f"Section: {result.section}")
    print(f"BGE Score: {result.rerank_score}")
    print(f"Title: {result.section_title}")
    print(f"Text: {result.text}")