import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class JinaEmbedder:
    def __init__(self):
        api_key = os.getenv("JINA_API_KEY")

        if not api_key:
            raise ValueError("JINA API KEY not found")
        self.client = OpenAI(api_key=api_key, base_url="https://api.jina.ai/v1")

        self.model = "jina-embeddings-v4"

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts, encoding_format="float")

        return [item.embedding for item in response.data]

    def embed_query(self, text:list[str])->list[float]:
        response = self.client.embeddings.create(model = self.model, input=[text], encoding_format="float")
        return response.data[0].embedding