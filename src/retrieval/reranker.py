import requests
import os

from dotenv import load_dotenv
from src.models.schemas import RetrievedChunk, RerankedChunk


load_dotenv()
JINA_RERANKER_MODEL = "jina-reranker-v3"
FINAL_K = 5

class JinaReranker:

    def __init__(self):
        self.api_key = os.getenv("JINA_API_KEY")

        if not self.api_key:
            raise ValueError("JINA_API_KEY not found in .env")

        self.model = "jina-reranker-v3"
        self.url = "https://api.jina.ai/v1/rerank"

    def rerank(
        self,
        query: str,
        chunks : list[RetrievedChunk],
        top_n: int = FINAL_K
    ) ->list[RerankedChunk]:
        
        if not chunks:
            return []

        documents = [
            chunk.text for chunk in chunks
        ]

        payload = {
            "model": JINA_RERANKER_MODEL,
            "query" : query,
            "documents": documents,
            "top_n": top_n,
            "return_documents": False
        }
        response = requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        reranked_results=[]

        for result in data["results"]:
            original_index = result["index"]
            rerank_score = result["relevance_score"]

            original_chunk = chunks[original_index]

            reranked_chunk = RerankedChunk(
                text=original_chunk.text,
                document=original_chunk.document,
                source=original_chunk.source,
                section=original_chunk.section,
                section_title=original_chunk.section_title,
                page_start=original_chunk.page_start,
                page_end=original_chunk.page_end,
                qdrant_score=original_chunk.qdrant_score,
                rerank_score=rerank_score
            )
            reranked_results.append(reranked_chunk)

        return reranked_results