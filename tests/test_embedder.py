from src.ingestion.embedder import JinaEmbedder


embedder = JinaEmbedder()

text = "Production database access requires security approval."

vector = embedder.embed_query(text)

print("Vector dimension:", len(vector))
print("First 10 values:", vector[:10])