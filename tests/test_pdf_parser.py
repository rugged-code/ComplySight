from src.ingestion.pdf_parser import parse_pdf


document = parse_pdf(
    "data/policies/vendor_management.pdf"
)

print("Document:", document.title)
print("Source:", document.source)

for section in document.sections:
    print("\n-----------------------------")
    print("Page:", section.page_start)
    print(section.content[:500])