import os
import requests
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
import uuid

load_dotenv()

COLLECTION_NAME="policylens_policies"
VECTOR_SIZE=2048


class QdrantStore:
    def __init__(self):
        self.url = os.getenv("QDRANT_URL")
        self.api_key = os.getenv("QDRANT_API_KEY")

        if not self.url:
            raise ValueError("QDRANT url not found")
        if not self.api_key:
            raise ValueError("QDRANT api key not found")

        self.client = QdrantClient(url=self.url, api_key=self.api_key, timeout=30, check_compatibility=False)

    def create_collection(self):
        if self.client.collection_exists(COLLECTION_NAME):
            return

        self.client.create_collection(
            collection_name=COLLECTION_NAME, 
            vectors_config=models.VectorParams(size=VECTOR_SIZE, distance= models.Distance.COSINE)
        )

    def get_chunks_by_document(self, document_name: str):
        endpoint = f"{self.url.rstrip('/')}/collections/{COLLECTION_NAME}/points/scroll"
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "filter": {
                "must": [
                    {
                        "key": "document",
                        "match": {"value": document_name}
                    }
                ]
            },
            "limit": 200,
            "with_payload": True,
            "with_vector": False,
        }
        for attempt in range(3):
            try:
                res = requests.post(endpoint, headers=headers, json=payload, timeout=15)
                if res.status_code == 200:
                    points_data = res.json().get("result", {}).get("points", [])
                    class SimplePoint:
                        def __init__(self, p):
                            self.payload = p.get("payload", {})
                    return [SimplePoint(p) for p in points_data]
            except Exception:
                if attempt == 2:
                    break
        try:
            points, _ = self.client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document",
                            match=models.MatchValue(value=document_name),
                        )
                    ]
                ),
                limit=200,
                with_payload=True,
                with_vectors=False,
            )
            return points
        except Exception:
            return []

    def add_documents(self, chunks, vectors):

        points = []

        for chunk, vector in zip(chunks, vectors):

            points.append(
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "text": chunk.text,
                        "document": chunk.document,
                        "source": chunk.source,
                        "section": chunk.section,
                        "section_title": chunk.section_title,
                        "page_start": chunk.page_start,
                        "page_end": chunk.page_end
                    }
                )
            )

        self.client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True,
        timeout=120,
)

        