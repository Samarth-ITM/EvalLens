"""
Unit tests for core/document_parser.py.

Verifies:
- TXT, MD, PDF, and DOCX text extraction
- Code file extraction across all supported programming languages
- Line numbers and page number tracking
- Word counting accuracy and multiple file aggregation
- 5,000-word limit enforcement
- Rejection of oversized submissions (> 5,000 words)
- 10 MB per-file size limit
- Rejection of unsupported file formats (ZIP, PPTX, image formats)
- Handling of PDFs without extractable text
"""

from __future__ import annotations

import io
from pathlib import Path
import pytest
import pypdf
import docx

from core.document_parser import (
    MAX_FILE_SIZE_BYTES,
    MAX_SUBMISSION_WORDS,
    check_submission_word_limit,
    count_words,
    parse_docx_file,
    parse_pdf_file,
    parse_text_content,
    parse_uploaded_file,
)


def create_sample_docx(text: str) -> bytes:
    """Helper to generate an in-memory docx binary."""
    doc = docx.Document()
    for paragraph in text.splitlines():
        if paragraph.strip():
            doc.add_paragraph(paragraph.strip())
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def create_sample_pdf(text: str) -> bytes:
    """Helper to generate a minimal valid PDF with extractable text."""
    # Escape parentheses for PDF text string
    escaped_text = text.replace("(", "\\(").replace(")", "\\)")
    stream_content = f"BT\n/F1 12 Tf\n100 700 Td\n({escaped_text}) Tj\nET"
    stream_len = len(stream_content)
    pdf_content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
5 0 obj
<< /Length {stream_len} >>
stream
{stream_content}
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000244 00000 n 
0000000318 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
400
%%EOF"""
    return pdf_content.encode("latin-1")


def create_blank_pdf() -> bytes:
    """Helper to create a PDF with no extractable text."""
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=300, height=300)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_txt_and_md_extraction() -> None:
    """Verify TXT and Markdown extraction preserves text and attaches line numbers."""
    content = "First line of essay\nSecond line of essay\nThird line."
    parsed_txt = parse_uploaded_file(content.encode("utf-8"), "essay.txt")
    assert parsed_txt.extension == ".txt"
    assert parsed_txt.word_count == 10
    assert parsed_txt.line_count == 3
    assert "L1: First line" in parsed_txt.formatted_text
    assert "L2: Second line" in parsed_txt.formatted_text

    parsed_md = parse_uploaded_file(b"# Header\n\nContent here.", "notes.md")
    assert parsed_md.extension == ".md"
    assert parsed_md.word_count == 4


def test_pdf_extraction_with_page_markers() -> None:
    """Verify PDF text extraction includes page markers."""
    pdf_bytes = create_sample_pdf("Sample Evaluation Paper Content")
    parsed = parse_uploaded_file(pdf_bytes, "paper.pdf")
    assert parsed.extension == ".pdf"
    assert "Sample Evaluation Paper Content" in parsed.raw_text
    assert "[Page 1]" in parsed.formatted_text
    assert parsed.word_count > 0


def test_scanned_pdf_warning() -> None:
    """Verify that a PDF without extractable text produces a clear explanation warning."""
    blank_pdf = create_blank_pdf()
    parsed = parse_uploaded_file(blank_pdf, "scanned_doc.pdf")
    assert parsed.word_count == 0
    assert any("scanned document or image-only PDF" in w for w in parsed.warnings)


def test_docx_extraction() -> None:
    """Verify DOCX text extraction."""
    docx_bytes = create_sample_docx("Paragraph 1 of Word document.\nParagraph 2 with details.")
    parsed = parse_uploaded_file(docx_bytes, "report.docx")
    assert parsed.extension == ".docx"
    assert "Paragraph 1" in parsed.raw_text
    assert "Paragraph 2" in parsed.raw_text
    assert parsed.word_count > 5


def test_code_file_extraction_supported_languages() -> None:
    """Verify that code files in all supported languages are parsed as text with line numbers."""
    code_samples = {
        "main.py": "def add(a, b):\n    return a + b",
        "app.js": "const x = 10;\nconsole.log(x);",
        "service.ts": "interface User { id: number; }\nconst u: User = { id: 1 };",
        "Main.java": "public class Main {\n    public static void main(String[] args) {}\n}",
        "solution.cpp": "#include <iostream>\nint main() { return 0; }",
        "header.h": "#ifndef HEADER_H\n#define HEADER_H\n#endif",
        "header.hpp": "#pragma once\nclass Engine {};",
        "schema.sql": "CREATE TABLE users (id INT PRIMARY KEY);",
        "data.json": '{"name": "EvalLens", "version": 1}',
        "index.html": "<!DOCTYPE html><html><body><h1>Title</h1></body></html>",
        "styles.css": "body { margin: 0; padding: 0; }",
    }

    for filename, code in code_samples.items():
        parsed = parse_uploaded_file(code.encode("utf-8"), filename)
        assert parsed.word_count > 0
        assert "L1: " in parsed.formatted_text
        assert parsed.metadata.get("is_code") is True


def test_unsupported_file_formats_rejected() -> None:
    """Verify that unsupported extensions (ZIP, PPTX, images, etc.) are strictly rejected."""
    forbidden_files = ["archive.zip", "slides.pptx", "photo.png", "scan.jpg", "program.exe"]
    for fname in forbidden_files:
        with pytest.raises(ValueError) as excinfo:
            parse_uploaded_file(b"dummy bytes", fname)
        assert "Unsupported file format" in str(excinfo.value)
        assert "ZIP, PPTX, image uploads, and OCR are not supported" in str(excinfo.value)


def test_file_size_limit_enforced() -> None:
    """Verify that files exceeding 10 MB are rejected."""
    large_bytes = b"x" * (MAX_FILE_SIZE_BYTES + 1024)
    with pytest.raises(ValueError) as excinfo:
        parse_uploaded_file(large_bytes, "toolarge.txt")
    assert "exceeds the 10 MB size limit" in str(excinfo.value)


def test_word_counting_and_5000_limit() -> None:
    """Verify word counting accuracy and rejection when exceeding 5,000 words."""
    # Under limit
    text_under = "word " * 4999
    assert count_words(text_under) == 4999
    is_valid, msg = check_submission_word_limit(4999)
    assert is_valid is True
    assert "within the 5,000-word limit" in msg

    # Exact limit
    is_valid_exact, _ = check_submission_word_limit(5000)
    assert is_valid_exact is True

    # Exceeding limit
    is_valid_over, err_msg = check_submission_word_limit(5001)
    assert is_valid_over is False
    assert "Submission rejected: Detected 5,001 words" in err_msg
    assert "exceeds the maximum limit of 5,000 words" in err_msg
