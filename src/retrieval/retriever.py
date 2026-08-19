from src.ingestion.embedder import JinaEmbedder
from src.ingestion.qdrant_store import QdrantStore
from src.models.schemas import RetrievedChunk


class PolicyRetriever:
    """
    Retrieves direct Qdrant matches only.

    Do not expand the most common document with every one of its sections.
    That behavior contaminated irrelevant cases with unrelated policy text.
    """

    def __init__(self, top_k: int = 30):
        self.embedder = JinaEmbedder()
        self.store = QdrantStore()
        self.top_k = top_k

    def retrieve(self, query: str) -> list[RetrievedChunk]:
        query_vector = self.embedder.embed_query(query)

        response = self.store.client.query_points(
            collection_name="policylens_policies",
            query=query_vector,
            limit=self.top_k,
            with_payload=True,
            timeout=120,
        )

        retrieved_chunks: list[RetrievedChunk] = []
        seen: set[tuple[str, str | None]] = set()

        for point in response.points:
            payload = point.payload

            key = (
                payload["document"],
                payload.get("section"),
            )

            if key in seen:
                continue

            seen.add(key)

            retrieved_chunks.append(
                RetrievedChunk(
                    text=payload["text"],
                    document=payload["document"],
                    source=payload["source"],
                    section=payload.get("section"),
                    section_title=payload.get("section_title"),
                    page_start=payload.get("page_start"),
                    page_end=payload.get("page_end"),
                    qdrant_score=float(point.score),
                )
            )

        return retrieved_chunks