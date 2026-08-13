from pathlib import Path
from src.ingestion.markdown_parser import parse_markdown
from src.ingestion.chunker import chunk_document
from src.ingestion.embedder import JinaEmbedder
from src.ingestion.qdrant_store import QdrantStore


POLICY_DIRECTORY= Path("data/policies")

def main():

    embedder = JinaEmbedder
    store = QdrantStore

    store.create_collection()

    total_chunks = 0

    policy_files = list(POLICY_DIRECTORY.glob("*.md"))

    print(f"Found {len(policy_files)} policy files.\n")

    for file in policy_files:
        print(f"Processing {file.name}")

        document = parse_markdown(str(file))

        chunks = chunk_document(document)

        texts = [chunk.text for chunk in chunks]

        vectors = embedder.embed_documents(texts)

        store.add_documents(chunks, vectors)
        print("  Uploaded to Qdrant cloud\n")

        total_chunks += len(chunks)

        print("Ingestion complete!")
        print(f"Total chunks: {total_chunks}")

if __name__ == "__main__":
    main()