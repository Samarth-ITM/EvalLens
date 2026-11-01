"""
Document Parser and Text Extraction for EvalLens.

Extracts text from supported documents and code files while preserving
page numbers (for PDFs), line numbers (for code/text), and extraction warnings.
Enforces strict 10 MB per-file and 5,000 total words submission limits.
"""

from __future__ import annotations

import io
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".pdf",
    ".docx",
    ".py",
    ".cpp",
    ".h",
    ".hpp",
    ".java",
    ".js",
    ".ts",
    ".json",
    ".html",
    ".css",
    ".sql",
}

CODE_EXTENSIONS = {
    ".py",
    ".cpp",
    ".h",
    ".hpp",
    ".java",
    ".js",
    ".ts",
    ".json",
    ".html",
    ".css",
    ".sql",
}

MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
MAX_SUBMISSION_WORDS: int = 5000


@dataclass
class ParsedDocument:
    """Represents the parsed content and metadata of a single file or pasted text."""

    filename: str
    extension: str
    raw_text: str
    formatted_text: str
    word_count: int
    line_count: int
    page_count: Optional[int] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


def count_words(text: str) -> int:
    """Count words in text using non-whitespace token extraction."""
    if not text:
        return 0
    return len(re.findall(r"\S+", text))


def check_submission_word_limit(total_words: int) -> Tuple[bool, str]:
    """
    Validate that total submission word count does not exceed 5,000 words.
    Returns (is_valid, message).
    """
    if total_words > MAX_SUBMISSION_WORDS:
        return (
            False,
            f"Submission rejected: Detected {total_words:,} words, which exceeds the maximum limit "
            f"of {MAX_SUBMISSION_WORDS:,} words. Please reduce your submission content.",
        )
    return True, f"Word count ({total_words:,} words) is within the {MAX_SUBMISSION_WORDS:,}-word limit."


def parse_text_content(
    text: str, filename: str = "pasted_text.txt", is_code: bool = False
) -> ParsedDocument:
    """
    Parse a string of text or code into a ParsedDocument, adding line numbers to formatted text.
    """
    clean_text = text.strip()
    words = count_words(clean_text)
    lines = clean_text.splitlines()
    line_count = len(lines) if clean_text else 0

    # Add line numbers for reference in code or text files
    formatted_lines = [f"L{idx+1}: {line}" for idx, line in enumerate(lines)]
    formatted_text = "\n".join(formatted_lines)

    warnings: List[str] = []
    if not clean_text:
        warnings.append("Text content is empty.")

    ext = Path(filename).suffix.lower() or ".txt"

    return ParsedDocument(
        filename=filename,
        extension=ext,
        raw_text=clean_text,
        formatted_text=formatted_text,
        word_count=words,
        line_count=line_count,
        page_count=None,
        warnings=warnings,
        metadata={"is_code": is_code},
    )


def parse_pdf_file(file_bytes: bytes, filename: str) -> ParsedDocument:
    """
    Extract readable text from a PDF file with page markers.
    """
    import pypdf

    warnings: List[str] = []
    page_texts: List[str] = []
    formatted_chunks: List[str] = []

    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        total_pages = len(reader.pages)

        for p_idx, page in enumerate(reader.pages):
            p_text = page.extract_text() or ""
            p_text_clean = p_text.strip()
            if p_text_clean:
                page_texts.append(p_text_clean)
                formatted_chunks.append(f"--- [Page {p_idx+1}] ---\n{p_text_clean}")
            else:
                formatted_chunks.append(f"--- [Page {p_idx+1}] (No extractable text) ---")

        raw_combined = "\n\n".join(page_texts).strip()
        formatted_combined = "\n\n".join(formatted_chunks).strip()

        if not raw_combined:
            warnings.append(
                "PDF contains no extractable text. It may be a scanned document or image-only PDF, "
                "which is not supported in this prototype."
            )

        words = count_words(raw_combined)
        lines = raw_combined.splitlines()

        return ParsedDocument(
            filename=filename,
            extension=".pdf",
            raw_text=raw_combined,
            formatted_text=formatted_combined,
            word_count=words,
            line_count=len(lines),
            page_count=total_pages,
            warnings=warnings,
            metadata={"pages": total_pages},
        )

    except Exception as e:
        warnings.append(f"Failed to read PDF file: {str(e)}")
        return ParsedDocument(
            filename=filename,
            extension=".pdf",
            raw_text="",
            formatted_text="",
            word_count=0,
            line_count=0,
            page_count=0,
            warnings=warnings,
        )


def parse_docx_file(file_bytes: bytes, filename: str) -> ParsedDocument:
    """
    Extract readable text from a Microsoft Word (.docx) file.
    """
    import docx

    warnings: List[str] = []
    extracted_paragraphs: List[str] = []

    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        for p in doc.paragraphs:
            txt = p.text.strip()
            if txt:
                extracted_paragraphs.append(txt)

        # Also extract table text
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    extracted_paragraphs.append(f"[Table Row]: {row_text}")

        raw_combined = "\n\n".join(extracted_paragraphs).strip()
        lines = raw_combined.splitlines()
        formatted_lines = [f"L{idx+1}: {line}" for idx, line in enumerate(lines)]
        formatted_combined = "\n".join(formatted_lines)

        if not raw_combined:
            warnings.append("DOCX file appears empty or contains no readable paragraphs.")

        words = count_words(raw_combined)

        return ParsedDocument(
            filename=filename,
            extension=".docx",
            raw_text=raw_combined,
            formatted_text=formatted_combined,
            word_count=words,
            line_count=len(lines),
            page_count=None,
            warnings=warnings,
            metadata={"paragraphs": len(extracted_paragraphs)},
        )

    except Exception as e:
        warnings.append(f"Failed to read DOCX file: {str(e)}")
        return ParsedDocument(
            filename=filename,
            extension=".docx",
            raw_text="",
            formatted_text="",
            word_count=0,
            line_count=0,
            page_count=None,
            warnings=warnings,
        )


def parse_uploaded_file(file_bytes: bytes, filename: str) -> ParsedDocument:
    """
    Main dispatch function to validate and extract text from an uploaded file.
    Enforces format restrictions and the 10 MB size limit.
    """
    # 1. Check file size
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        mb = len(file_bytes) / (1024 * 1024)
        raise ValueError(
            f"File '{filename}' ({mb:.2f} MB) exceeds the 10 MB size limit. Please upload a smaller file."
        )

    # 2. Check extension
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file format '{ext}' for file '{filename}'. "
            "Supported formats: TXT, MD, PDF, DOCX, PY, CPP, H, HPP, JAVA, JS, TS, JSON, HTML, CSS, SQL. "
            "Note: ZIP, PPTX, image uploads, and OCR are not supported in this prototype."
        )

    # 3. Parse based on extension
    if ext == ".pdf":
        return parse_pdf_file(file_bytes, filename)
    elif ext == ".docx":
        return parse_docx_file(file_bytes, filename)
    else:
        # Text or code files
        # Attempt UTF-8 decode, fallback to latin-1
        try:
            decoded_text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                decoded_text = file_bytes.decode("latin-1")
            except Exception as e:
                raise ValueError(f"Could not decode text file '{filename}': {e}")

        is_code = ext in CODE_EXTENSIONS
        return parse_text_content(decoded_text, filename=filename, is_code=is_code)
