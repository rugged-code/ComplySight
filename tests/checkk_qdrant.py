from src.ingestion.qdrant_store import QdrantStore

store = QdrantStore()

print(store.client.count(
    collection_name="policylens_policies",
    exact=True
))