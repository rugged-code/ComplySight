from src.ingestion.qdrant_store import QdrantStore
from src.ingestion.embedder import JinaEmbedder
from src.models.schemas import RetrievedChunk

class PolicyRetriever:
    def __init__(self, top_k: int = 30):
        self.embedder = JinaEmbedder()
        self.store = QdrantStore()

        self.top_k = top_k

    def retrieve(self, query: str) -> list[RetrievedChunk]:

        query_vector = self.embedder.embed_query(query)

        results = self.store.client.query_points(
            collection_name = "policylens_policies",
            query=query_vector, 
            limit = self.top_k,
            with_payload=True
        )

        retrieved_chunks = []
        for result in results.points:
            payload = result.payload

            chunk = RetrievedChunk(
                text = payload["text"],
                document= payload["document"],
                source=payload["source"],
                section=payload["section"],
                section_title=payload["section_title"],
                page_start=payload.get("page_start"),
                page_end=payload.get("page_end"),
                qdrant_score=result.score
            )

            retrieved_chunks.append(chunk)

        return retrieved_chunks 