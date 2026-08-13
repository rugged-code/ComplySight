from src.ingestion.qdrant_store import QdrantStore


store = QdrantStore()

print("Connected to Qdrant Cloud")

store.create_collection()

print("Collection ready")