from src.models.schemas import ParsedDocument, ParsedSection


def test_parsed_document_and_section():
    section = ParsedSection(
        title="Access Control",
        number="4.2",
        content="Production access requires manager and security approval.",
        page_start=7,
        page_end=7,
    )

    document = ParsedDocument(
        title="Security Policy",
        source="security_policy.pdf",
        file_type="pdf",
        sections=[section],
    )

    assert document.title == "Security Policy"
    assert document.source == "security_policy.pdf"
    assert document.file_type == "pdf"
    assert len(document.sections) == 1
    sec = document.sections[0]
    assert isinstance(sec, ParsedSection)
    assert sec.title == "Access Control"
    assert sec.number == "4.2"
    assert sec.page_start == 7
    assert sec.page_end == 7