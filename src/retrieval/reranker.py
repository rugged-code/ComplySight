import requests
import os

from dotenv import load_dotenv
from openai import OpenAI


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
        results,
        top_n: int = FINAL_K
    ):
        if not results:
            return []

        documents = [
            result.payload["text"]
            for result in results
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
            score = result["relevance_score"]

            original_result = results[original_index]

            reranked_results.append({
                "rerank_score": score,
                "payload": original_result.payload,
                "qdrant_score": original_result.score,
            })

        return reranked_results