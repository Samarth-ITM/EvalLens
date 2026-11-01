"""
Unit tests for submission processing edge cases and boundary conditions.

Covers:
- Empty text submission rejection
- Empty files (0 bytes)
- Corrupted PDF handling
- PDF with no extractable text (e.g. image-only)
- Invalid / corrupted DOCX handling
- Unsupported file extensions (.zip, .exe, .png)
- Duplicate filenames in multi-file upload
- Multiple simultaneous uploads
- Unicode content (emojis, non-ASCII accents, CJK characters)
- Very long lines (10,000+ characters)
- Boundary condition: exactly 5,000 words (accepted)
- Boundary condition: 5,001 words (rejected)
- Files exceeding 10 MB limit (rejected)
- Empty reference material (valid)
- Missing optional instructions (valid)
"""

from __future__ import annotations

import io
import pytest
from pypdf import PdfWriter

from core.document_parser import (
    MAX_FILE_SIZE_BYTES,
    MAX_SUBMISSION_WORDS,
    count_words,
    parse_uploaded_file,
    parse_text_content,
    check_submission_word_limit,
)
from core.submission import (
    prepare_submission,
    sanitize_filename,
)


def test_empty_text_and_empty_files_rejected() -> None:
    """Verify that empty text or no uploads raise ValueError."""
    with pytest.raises(ValueError, match="Please provide at least one text submission or upload a supported file"):
        prepare_submission(title="Empty Submission", pasted_text="", uploaded_files=[])

    with pytest.raises(ValueError, match="Please provide at least one text submission or upload a supported file"):
        prepare_submission(title="Whitespace Submission", pasted_text="   \n\t  ", uploaded_files=[])


def test_empty_file_zero_bytes() -> None:
    """Verify that a zero-byte file parses gracefully without crashing and notes 0 words."""
    parsed = parse_uploaded_file(b"", "empty.txt")
    assert parsed.word_count == 0
    assert parsed.extension == ".txt"
    assert parsed.formatted_text == ""


def test_corrupted_pdf_handling() -> None:
    """Verify that corrupted PDF bytes generate a clear extraction warning rather than crashing."""
    corrupted_bytes = b"%PDF-1.4\nInvalid corrupted binary content here..."
    parsed = parse_uploaded_file(corrupted_bytes, "broken.pdf")
    assert parsed.word_count == 0
    assert any("Failed to read PDF file" in w for w in parsed.warnings)


def test_pdf_with_no_extractable_text() -> None:
    """Verify that a valid PDF with blank/image-only pages produces a scanned PDF warning."""
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    pdf_bytes = io.BytesIO()
    writer.write(pdf_bytes)

    parsed = parse_uploaded_file(pdf_bytes.getvalue(), "blank.pdf")
    assert parsed.word_count == 0
    assert any("scanned" in w.lower() for w in parsed.warnings)


def test_invalid_docx_handling() -> None:
    """Verify that corrupted DOCX bytes produce a clear extraction warning rather than crashing."""
    corrupted_bytes = b"PK\x03\x04not a valid docx zip archive"
    parsed = parse_uploaded_file(corrupted_bytes, "broken.docx")
    assert parsed.word_count == 0
    assert any("Failed to read DOCX file" in w for w in parsed.warnings)


def test_unsupported_extensions() -> None:
    """Verify that unsupported extensions (.zip, .exe, .png) are rejected with ValueError."""
    for ext in ["archive.zip", "binary.exe", "image.png", "data.tar.gz"]:
        with pytest.raises(ValueError, match="Unsupported file format"):
            parse_uploaded_file(b"data", ext)


def test_file_larger_than_10mb_rejected() -> None:
    """Verify that files exceeding the 10 MB limit are rejected with ValueError."""
    oversized_bytes = b"x" * (MAX_FILE_SIZE_BYTES + 1024)
    with pytest.raises(ValueError, match="exceeds the 10 MB size limit"):
        parse_uploaded_file(oversized_bytes, "huge.txt")


def test_duplicate_filenames_disambiguation() -> None:
    """Verify that duplicate filenames in multiple uploads are disambiguated."""
    file1 = ("main.py", b"def a(): pass")
    file2 = ("main.py", b"def b(): pass")

    prepared = prepare_submission(
        title="Duplicate Files Submission",
        uploaded_files=[file1, file2],
    )

    filenames = [doc.filename for doc in prepared.documents]
    assert len(filenames) == 2
    assert "main.py" in filenames
    assert "main_2.py" in filenames


def test_multiple_uploads_combined() -> None:
    """Verify that multiple valid files of different types are aggregated properly."""
    f1 = ("notes.txt", b"First file text")
    f2 = ("script.py", b"print('hello world')")
    f3 = ("style.css", b"body { margin: 0; }")

    prepared = prepare_submission(
        title="Multi Upload",
        pasted_text="Pasted report overview",
        uploaded_files=[f1, f2, f3],
    )

    assert len(prepared.documents) == 4  # 1 pasted + 3 uploaded
    assert prepared.total_words > 0
    assert "=== Source: notes.txt" in prepared.combined_submission_text
    assert "=== Source: script.py" in prepared.combined_submission_text
    assert "=== Source: style.css" in prepared.combined_submission_text


def test_unicode_content_and_emojis() -> None:
    """Verify that Unicode content (emojis, accents, CJK) parses and counts correctly."""
    unicode_text = "Evaluation with Unicode: 🌟 Évaluation naïve 机器学习 and symbols ∑(x) = y."
    parsed = parse_text_content(unicode_text, "unicode.txt", is_code=False)
    assert parsed.word_count > 0
    assert "🌟" in parsed.formatted_text
    assert "Évaluation" in parsed.formatted_text
    assert "机器学习" in parsed.formatted_text


def test_very_long_lines() -> None:
    """Verify that files with very long lines (e.g. minified code or long strings) don't crash."""
    long_line = "variable = '" + ("A" * 15000) + "';"
    parsed = parse_text_content(long_line, "long_line.js", is_code=True)
    assert parsed.word_count > 0
    assert len(parsed.formatted_text) >= 15000


def test_exactly_5000_words_passes() -> None:
    """Verify that a submission with exactly 5,000 words passes validation."""
    words_5000 = "word " * 5000
    is_valid, msg = check_submission_word_limit(5000)
    assert is_valid is True
    assert "within the 5,000-word limit" in msg

    prepared = prepare_submission(
        title="Exact 5000 Words",
        pasted_text=words_5000,
    )
    assert prepared.total_words == 5000


def test_5001_words_rejected() -> None:
    """Verify that a submission with 5,001 words is rejected with clear message."""
    words_5001 = "word " * 5001
    is_valid, msg = check_submission_word_limit(5001)
    assert is_valid is False
    assert "maximum limit of 5,000 words" in msg
    assert "Detected 5,001 words" in msg

    with pytest.raises(ValueError) as excinfo:
        prepare_submission(
            title="Exceed 5000 Words",
            pasted_text=words_5001,
        )
    assert "5,001 words" in str(excinfo.value)
    assert "5,000 words" in str(excinfo.value)
    assert "5,001 words" in str(excinfo.value)
    assert "limit of 5,000 words" in str(excinfo.value)


def test_empty_reference_material_and_missing_instructions_valid() -> None:
    """Verify that empty reference material and instructions are valid and cleanly treated as None."""
    prepared = prepare_submission(
        title="Minimal Submission",
        instructions="",
        reference_material=None,
        pasted_text="Valid minimal submission content.",
    )
    assert prepared.instructions is None
    assert prepared.reference_material is None
    assert prepared.total_words == 4
