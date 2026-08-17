from sentence_transformers import CrossEncoder

from src.models.schemas import RetrievedChunk, RerankedChunk


class BGEReranker:

    def __init__(self):

        self.model = CrossEncoder(
            "BAAI/bge-reranker-v2-m3"
        )

    def rerank(
        self,
        query: str,
        chunks: list[RetrievedChunk],
        top_n: int = 5
    ) -> list[RerankedChunk]:

        if not chunks:
            return []

        # Create query-document pairs
        pairs = [
            [query, chunk.text]
            for chunk in chunks
        ]

        # Get relevance scores
        scores = self.model.predict(pairs)

        # Attach scores to chunks
        scored_chunks = list(zip(chunks, scores))

        # Highest score first
        scored_chunks.sort(
            key=lambda x: x[1],
            reverse=True
        )

        # Take top N
        top_chunks = scored_chunks[:top_n]

        # Convert to RerankedChunk
        results = []

        for chunk, score in top_chunks:

            results.append(
                RerankedChunk(
                    text=chunk.text,
                    document=chunk.document,
                    source=chunk.source,
                    section=chunk.section,
                    section_title=chunk.section_title,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    qdrant_score=chunk.score,
                    rerank_score=float(score)
                )
            )

        return results