from src.ingestion.markdown_parser import parse_markdown
from src.ingestion.chunker import chunk_document


document = parse_markdown(
    "data/policies/vendor_management.md"
)

chunks = chunk_document(document)

print("Total chunks:", len(chunks))

for i, chunk in enumerate(chunks, start=1):
    print("\n==============================")
    print("Chunk:", i)
    print("Document:", chunk.document)
    print("Section:", chunk.section)
    print("Title:", chunk.section_title)
    print("Text length:", len(chunk.text))
    print("Text:")
    print(chunk.text)