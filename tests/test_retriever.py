from src.retrieval.retriever import PolicyRetriever

retriever = PolicyRetriever()

query = """
I need production database access for debugging
a customer issue.
"""

# query = "Vendor Risk Assessment requirements for a new vendor"
# query = "Information Security Addendum required when vendor processes Confidential data"
# query = "CFO and Head of Procurement approval for vendor contracts over $50,000"

results = retriever.retrieve(query)

print(f"Retrieved {len(results)} results\n")
print("Requested top_k:", retriever.top_k)
print("Actual results:", len(results))

for i, result in enumerate(results, start=1):

    print("=" * 60)
    print(f"Result {i}")
    print("Score:", result.score)

    payload = result.payload

    print("Policy:", payload.get("document"))
    print("Section:", payload.get("section"))
    print("Section title:", payload.get("section_title"))
    print("Source:", payload.get("source"))

    print("\nText:")
    print(payload.get("text"))
