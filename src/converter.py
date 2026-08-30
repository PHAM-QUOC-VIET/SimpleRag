"""Convert the two Land Law document layouts into a shared JSON schema."""

import json
import re
from pathlib import Path
from typing import Any, Mapping

import pdfplumber


ARTICLE_PATTERN = re.compile(r"Điều\s+(\d+)\.\s*([^\n]+)")
ARTICLE_POSITION_PATTERN = re.compile(r"^Điều\s+\d+\.", re.MULTILINE)
CLAUSE_PATTERN = re.compile(
    r"^\s*(\d+)\.\s+(.+?)(?=^\s*\d+\.\s|^Điều\s+\d+\.|^Mục\s+\d+\.?\s|^Chương\s+[IVXLCDM]+\s*$|\Z)",
    re.MULTILINE | re.DOTALL,
)
POINT_PATTERN = re.compile(
    r"^\s*([a-zđ])\)\s+(.+?)(?=^\s*[a-zđ]\)\s|^\s*\d+\.\s|^Điều\s+\d+\.|^Mục\s+\d+\.?\s|^Chương\s+[IVXLCDM]+\s*$|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)


# The two source PDFs use different chapter and section layouts.
LEGACY_CHAPTER_PATTERN = re.compile(
    r"^Chương\s+([IVXLCDM]+)\s*$\n^([^\n]+)",
    re.MULTILINE | re.IGNORECASE,
)
LEGACY_SECTION_PATTERN = re.compile(
    r"^Mục\s+(\d+)\.\s*(.+?)(?=^Mục\s+\d+\.|^Điều\s+\d+\.|^Chương\s+[IVXLCDM]+\s*$|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)
CURRENT_CHAPTER_PATTERN = re.compile(
    r"^Chương\s+([IVXLCDM]+)\s*$\n^([^\n]+)",
    re.MULTILINE | re.IGNORECASE,
)
CURRENT_SECTION_PATTERN = re.compile(
    r"^Mục\s+(\d+)\.?\s*(.+?)(?=^Mục\s+\d+\.?\s|^Điều\s+\d+\.|^Chương\s+[IVXLCDM]+\s*$|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)


RECORD_FIELDS = (
    "document_name",
    "vbhn_number",
    "issue_date",
    "effective_date",
    "issuing_agency",
    "chapter_number",
    "chapter_title",
    "section_number",
    "section_title",
    "article_number",
    "article_title",
    "clause_number",
    "clause_content",
    "point_number",
    "point_content",
    "chunk_id",
    "text",
    "citation",
)


def clean_text(value: str | None) -> str:
    """Normalize whitespace without changing Vietnamese legal content."""
    if not value:
        return ""
    value = re.sub(r"CÔNG BÁO/Số.*?Ngày.*?\d+", "", value)
    value = re.sub(r"[\r\n\t]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def pdf_to_txt(pdf_path: Path, txt_path: Path) -> None:
    """Extract all available page text from a PDF."""
    with pdfplumber.open(pdf_path) as pdf_document:
        with txt_path.open("w", encoding="utf-8") as text_file:
            for page in pdf_document.pages:
                page_text = page.extract_text()
                if page_text:
                    text_file.write(page_text + "\n")
    print(f"PDF to TXT conversion completed: {txt_path}")


def make_record(
    metadata: Mapping[str, Any],
    chapter_number: str,
    chapter_title: str,
    section_number: str | None,
    section_title: str | None,
    article_number: int,
    article_title: str,
    clause_number: int | None,
    clause_content: str,
    point_number: str | None,
    point_content: str | None,
) -> dict[str, Any]:
    """Create one complete, consistently ordered output record."""
    clause_content = clean_text(clause_content)
    point_content = clean_text(point_content)
    article_text = f"Điều {article_number}. {article_title}"
    text_parts = [article_text]
    citation_parts = [str(metadata["document_name"]), f"Điều {article_number}"]

    if clause_number is not None:
        text_parts.append(f"Khoản {clause_number}. {clause_content}")
        citation_parts.append(f"Khoản {clause_number}")
    elif clause_content:
        text_parts.append(clause_content)

    if point_number:
        text_parts.append(f"Điểm {point_number}. {point_content}")
        citation_parts.append(f"Điểm {point_number}")

    text = clean_text(" ".join(text_parts))

    record = {
        **metadata,
        "chapter_number": chapter_number,
        "chapter_title": chapter_title,
        "section_number": section_number,
        "section_title": section_title,
        "article_number": article_number,
        "article_title": article_title,
        "clause_number": clause_number,
        "clause_content": clause_content,
        "point_number": point_number,
        "point_content": point_content or None,
        "chunk_id": f"{metadata['vbhn_number']}-article-{article_number}"
        + (f"-clause-{clause_number}" if clause_number is not None else "")
        + (f"-point-{point_number}" if point_number else ""),
        "text": text,
        "citation": ", ".join(citation_parts),
    }
    return {field: record.get(field) for field in RECORD_FIELDS}


def find_context(
    full_text: str,
    position: int,
    chapter_pattern: re.Pattern[str],
    section_pattern: re.Pattern[str],
) -> tuple[str, str, str | None, str | None]:
    """Find the latest chapter and section before an article."""
    chapters = [match for match in chapter_pattern.finditer(full_text) if match.start() < position]
    chapter = chapters[-1] if chapters else None
    chapter_number = clean_text(chapter.group(1)) if chapter else ""
    chapter_title = clean_text(chapter.group(2)) if chapter else ""
    chapter_start = chapter.start() if chapter else 0
    sections = [
        match
        for match in section_pattern.finditer(full_text)
        if chapter_start <= match.start() < position
    ]
    section = sections[-1] if sections else None
    section_number = clean_text(section.group(1)) if section else None
    section_title = clean_text(section.group(2)) if section else None
    return chapter_number, chapter_title, section_number, section_title


def parse_articles(
    full_text: str,
    metadata: Mapping[str, Any],
    chapter_pattern: re.Pattern[str],
    section_pattern: re.Pattern[str],
) -> list[dict[str, Any]]:
    """Parse article boundaries and preserve complete clause/point content."""
    article_positions = list(ARTICLE_POSITION_PATTERN.finditer(full_text))
    records: list[dict[str, Any]] = []

    for index, article_position in enumerate(article_positions):
        start = article_position.start()
        end = article_positions[index + 1].start() if index + 1 < len(article_positions) else len(full_text)
        article_segment = full_text[start:end]
        article_match = ARTICLE_PATTERN.search(article_segment)
        if not article_match:
            continue

        article_number = int(article_match.group(1))
        article_title = clean_text(article_match.group(2))
        article_body = article_segment[article_match.end():]
        chapter_number, chapter_title, section_number, section_title = find_context(
            full_text, start, chapter_pattern, section_pattern
        )
        clauses = list(CLAUSE_PATTERN.finditer(article_body))

        if not clauses:
            records.append(make_record(
                metadata, chapter_number, chapter_title, section_number, section_title,
                article_number, article_title, None, article_body, None, None,
            ))
            continue

        for clause in clauses:
            clause_number = int(clause.group(1))
            clause_content = clause.group(2)
            points = list(POINT_PATTERN.finditer(clause_content))
            content_before_points = clause_content[:points[0].start()] if points else clause_content

            if not points:
                records.append(make_record(
                    metadata, chapter_number, chapter_title, section_number, section_title,
                    article_number, article_title, clause_number, clause_content, None, None,
                ))
                continue

            for point_index, point in enumerate(points):
                point_end = points[point_index + 1].start() if point_index + 1 < len(points) else len(clause_content)
                point_content = clause_content[point.start():point_end]
                point_match = POINT_PATTERN.match(point_content)
                if not point_match:
                    continue
                records.append(make_record(
                    metadata, chapter_number, chapter_title, section_number, section_title,
                    article_number, article_title, clause_number, content_before_points,
                    clean_text(point_match.group(1)), point_match.group(2),
                ))

    for chunk_index, record in enumerate(records, start=1):
        record["chunk_id"] = f"{record['chunk_id']}-chunk-{chunk_index:05d}"

    return records


def parse_legacy_document(txt_path: Path, metadata: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Parse the older PDF layout with multi-line section headings."""
    full_text = txt_path.read_text(encoding="utf-8")
    full_text = re.sub(r"\r\n?", "\n", full_text)
    return parse_articles(full_text, metadata, LEGACY_CHAPTER_PATTERN, LEGACY_SECTION_PATTERN)


def parse_current_document(txt_path: Path, metadata: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Parse the newer PDF layout with same-line section headings."""
    full_text = txt_path.read_text(encoding="utf-8")
    full_text = re.sub(r"CÔNG BÁO/Số.*?Ngày.*?\d+\s*\n?", "", full_text)
    full_text = re.sub(r"\r\n?", "\n", full_text)
    return parse_articles(full_text, metadata, CURRENT_CHAPTER_PATTERN, CURRENT_SECTION_PATTERN)


def write_json(records: list[dict[str, Any]], output_path: Path) -> None:
    """Write records as UTF-8 JSON."""
    output_path.write_text(json.dumps(records, ensure_ascii=False, indent=4), encoding="utf-8")
    print(f"TXT to JSON conversion completed: {output_path}")


def merge_json_files(input_folder: Path, output_file: Path) -> None:
    """Merge generated JSON files without recursively including merged.json."""
    merged: list[dict[str, Any]] = []
    for json_file in input_folder.glob("*.json"):
        if json_file.resolve() == output_file.resolve():
            continue
        merged.extend(json.loads(json_file.read_text(encoding="utf-8")))
    output_file.write_text(json.dumps(merged, ensure_ascii=False, indent=4), encoding="utf-8")
    print(f"Merged JSON file created: {output_file}")


def run_converter() -> None:
    """Convert both source documents and create the merged dataset."""
    data_directory = Path(__file__).resolve().parent.parent / "Data"
    documents = [
        {
            "pdf_name": "133-vbhn-vpqh.pdf",
            "txt_name": "133-vbhn-vpqh.txt",
            "json_name": "133-vbhn-vpqh.json",
            "parser": parse_current_document,
            "metadata": {
                "document_name": "Văn bản hợp nhất Luật Đất đai số 44/VBHN-VPQH",
                "vbhn_number": "44/VBHN-VPQH",
                "issue_date": "16 tháng 03 năm 2026",
                "effective_date": "16 tháng 03 năm 2026",
                "issuing_agency": "Văn phòng Quốc hội",
            },
        },
        {
            "pdf_name": "Luat-Dat-dai-2013-sua-doi-bo-sung-2018.pdf",
            "txt_name": "Luat-Dat-dai-2013-sua-doi-bo-sung-2018.txt",
            "json_name": "Luat-Dat-dai-2013-sua-doi-bo-sung-2018.json",
            "parser": parse_legacy_document,
            "metadata": {
                "document_name": "Văn bản hợp nhất Luật Đất đai (sửa đổi, bổ sung 2018)",
                "vbhn_number": "21/VBHN-VPQH",
                "issue_date": "10 tháng 12 năm 2018",
                "effective_date": "01 tháng 01 năm 2019",
                "issuing_agency": "Văn phòng Quốc hội",
            },
        },
    ]

    for document in documents:
        pdf_path = data_directory / document["pdf_name"]
        txt_path = data_directory / document["txt_name"]
        json_path = data_directory / document["json_name"]
        if not pdf_path.is_file():
            raise FileNotFoundError(f"Input PDF not found: {pdf_path}")
        pdf_to_txt(pdf_path, txt_path)
        records = document["parser"](txt_path, document["metadata"])
        write_json(records, json_path)
        print(f"Records written: {len(records)}")

    merge_json_files(data_directory, data_directory / "merged.json")


if __name__ == "__main__":
    run_converter()
