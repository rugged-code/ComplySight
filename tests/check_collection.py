from src.ingestion.qdrant_store import QdrantStore

store = QdrantStore()

info = store.client.get_collection("policylens_policies")

print("Points in collection:", info.points_count)