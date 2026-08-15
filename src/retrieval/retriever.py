from src.ingestion.qdrant_store import QdrantStore
from src.ingestion.embedder import JinaEmbedder

class PolicyRetriever:
    def __init__(self, top_k: int = 30):
        self.embedder = JinaEmbedder()
        self.store = QdrantStore()

        self.top_k = top_k

    def retrieve(self, query: str):

        query_vector = self.embedder.embed_query(query)

        results = self.store.client.query_points(
            collection_name = "policylens_policies",
            query=query_vector, 
            limit = self.top_k,
            with_payload=True
        )
        return results.points