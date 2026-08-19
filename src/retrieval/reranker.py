import os

import requests
from dotenv import load_dotenv

from src.models.schemas import RetrievedChunk, RerankedChunk


load_dotenv()

JINA_RERANKER_MODEL = "jina-reranker-v2-base-multilingual"
JINA_RERANK_URL = "https://api.jina.ai/v1/rerank"


class JinaReranker:
    def __init__(self):
        self.api_key = os.getenv("JINA_API_KEY")

        if not self.api_key:
            raise ValueError("JINA_API_KEY not found in .env")

        self.model = JINA_RERANKER_MODEL
        self.url = JINA_RERANK_URL

    def rerank(
        self,
        query: str,
        chunks: list[RetrievedChunk],
        top_n: int = 8,
    ) -> list[RerankedChunk]:
        if not chunks:
            return []

        payload = {
            "model": self.model,
            "query": query,
            "documents": [chunk.text for chunk in chunks],
            "top_n": min(top_n, len(chunks)),
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        response = requests.post(
            self.url,
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        reranked_chunks: list[RerankedChunk] = []

        for result in results:
            index = result["index"]

            if index < 0 or index >= len(chunks):
                raise ValueError(
                    f"Jina returned invalid result index {index} "
                    f"for {len(chunks)} chunks"
                )

            original_chunk = chunks[index]

            reranked_chunks.append(
                RerankedChunk(
                    text=original_chunk.text,
                    document=original_chunk.document,
                    source=original_chunk.source,
                    section=original_chunk.section,
                    section_title=original_chunk.section_title,
                    page_start=original_chunk.page_start,
                    page_end=original_chunk.page_end,
                    qdrant_score=original_chunk.qdrant_score,
                    rerank_score=float(result["relevance_score"]),
                )
            )

        return reranked_chunks