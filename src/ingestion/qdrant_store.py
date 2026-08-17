import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
import uuid

load_dotenv()

COLLECTION_NAME="policylens_policies"
VECTOR_SIZE=2048


class QdrantStore:
    def __init__(self):
        url = os.getenv("QDRANT_URL")
        api_key = os.getenv("QDRANT_API_KEY")

        if not url:
            raise ValueError("QDRANT url not found")
        if not api_key:
            raise ValueError("QDRANT api key not found")

        self.client = QdrantClient(url=url, api_key=api_key)

    def create_collection(self):
        if self.client.collection_exists(COLLECTION_NAME):
            return

        self.client.create_collection(
            collection_name=COLLECTION_NAME, 
            vectors_config=models.VectorParams(size=VECTOR_SIZE, distance= models.Distance.COSINE)
        )

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

        