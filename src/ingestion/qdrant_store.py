import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

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

        