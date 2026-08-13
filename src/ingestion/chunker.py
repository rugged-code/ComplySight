from src.models.schemas import ParsedDocument, DocumentChunk

def chunk_document(document: ParsedDocument, chunk_size: int = 1500, overlap : int = 300) -> list[DocumentChunk]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than the chunk size")

    chunks = []

    for section in document.sections:

        text = section.content.strip()
        start = 0

        while start < len(text):
            end = start + chunk_size

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(DocumentChunk(
                    text = chunk_text, 
                    document = document.title,
                    source = document.source,
                    section = section.number,
                    section_title = section.title,
                    page_start = section.page_start,
                    page_end = section.page_end,
                ))
            start += chunk_size - overlap

    return chunks