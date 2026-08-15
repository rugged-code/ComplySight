from src.ingestion.qdrant_store import QdrantStore


store = QdrantStore()

results = store.client.scroll(
    collection_name="policylens_policies",
    limit=100,
    with_payload=True
)

points = results[0]

for point in points:

    payload = point.payload

    if payload.get("section") in ["4.1", "4.2", "4.3"]:

        print("\n============================")
        print("Section:", payload.get("section"))
        print("Title:", payload.get("section_title"))
        print("Text:")
        print(payload.get("text"))