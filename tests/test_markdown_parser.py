from src.ingestion.markdown_parser import parse_markdown


document = parse_markdown(
    "data/policies/vendor_management.md"
)

print("\nDocument:")
print(document.title)

print("\nSource:")
print(document.source)

print("\nSections:")

for section in document.sections:
    print("-----------------------------")
    print("Number:", section.number)
    print("Title:", section.title)
    print("Content:")
    print(section.content[:300])