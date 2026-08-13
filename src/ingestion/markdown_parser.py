from pathlib import Path
import re

from src.models.schemas import ParsedDocument, ParsedSection


def parse_markdown(file_path: str) -> ParsedDocument:
    path = Path(file_path)

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    title = path.stem.replace("_", " ").title()

    sections = []
    current_section = None

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Markdown heading
        match = re.match(r"^(#{1,6})\s+(.+)$", line)

        if match:
            heading = match.group(2).strip()

            # Try to extract a section number if one exists
            number_match = re.match(
                r"^(\d+(?:\.\d+)*)\.?\s+(.*)$",
                heading
            )

            if number_match:
                number = number_match.group(1)
                section_title = number_match.group(2).strip()
            else:
                number = None
                section_title = heading

            if current_section:
                sections.append(current_section)

            current_section = ParsedSection(
                title=section_title,
                number=number,
                content=""
            )

        elif current_section:
            current_section.content += line + "\n"

    if current_section:
        sections.append(current_section)

    return ParsedDocument(
        title=title,
        source=path.name,
        file_type="markdown",
        sections=sections
    )