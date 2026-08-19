from qdrant_client import QdrantClient, models
import os
from dotenv import load_dotenv

load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

client.create_payload_index(
    collection_name="policylens_policies",
    field_name="document",
    field_schema=models.PayloadSchemaType.KEYWORD,
)

print("Index on 'document' created successfully")