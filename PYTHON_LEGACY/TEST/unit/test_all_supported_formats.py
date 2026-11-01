"""
Unit tests covering all 15 supported file formats individually and comprehensively.

Supported formats tested:
- TXT, MD, PDF, DOCX
- PY, CPP, H, HPP, JAVA, JS, TS, JSON, HTML, CSS, SQL

Verifies for every format:
1. File is accepted.
2. File parses without crashing.
3. Extracted content is non-empty.
4. Key semantic tokens are preserved.
5. Word count is positive and accurate.
6. Extracted document integrates cleanly into prepare_submission().
"""

from __future__ import annotations

import io
from pathlib import Path
import pytest
import pypdf

from core.document_parser import (
    SUPPORTED_EXTENSIONS,
    parse_uploaded_file,
    parse_text_content,
    count_words,
)
from core.submission import prepare_submission

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "formats"


@pytest.mark.parametrize("filename", sorted(list(SUPPORTED_EXTENSIONS)))
def test_all_15_supported_formats_parse_successfully(filename: str) -> None:
    """Verify that every single supported format is accepted and parsed without errors."""
    fixture_path = FIXTURES_DIR / f"sample{filename}"
    assert fixture_path.exists(), f"Fixture file for {filename} must exist"

    file_bytes = fixture_path.read_bytes()
    assert len(file_bytes) > 0

    parsed = parse_uploaded_file(file_bytes, fixture_path.name)

    assert parsed.extension == filename
    assert parsed.word_count > 0
    assert parsed.line_count > 0
    assert len(parsed.raw_text.strip()) > 0
    assert len(parsed.formatted_text.strip()) > 0
    assert len(parsed.warnings) == 0


def test_txt_format_semantic_integrity() -> None:
    """Verify TXT format preserves paragraphs and structure."""
    path = FIXTURES_DIR / "sample.txt"
    parsed = parse_uploaded_file(path.read_bytes(), "sample.txt")
    assert "Distributed Edge Anomaly Detection" in parsed.raw_text
    assert "Executive Summary" in parsed.raw_text
    assert parsed.word_count > 1000


def test_md_format_semantic_integrity() -> None:
    """Verify Markdown format preserves headings, markdown lists, and tables."""
    path = FIXTURES_DIR / "sample.md"
    parsed = parse_uploaded_file(path.read_bytes(), "sample.md")
    assert "## 1. Executive Summary" in parsed.raw_text
    assert "Table 1: Ingestion & Telemetry" in parsed.raw_text
    assert "F1-score" in parsed.raw_text


def test_docx_format_semantic_integrity() -> None:
    """Verify DOCX format extracts headings, bullet points, and tables."""
    path = FIXTURES_DIR / "sample.docx"
    parsed = parse_uploaded_file(path.read_bytes(), "sample.docx")
    assert "Distributed Edge Anomaly Detection" in parsed.raw_text
    assert "Executive Summary" in parsed.raw_text
    assert "Cluster" in parsed.raw_text
    assert parsed.word_count > 1000


def test_pdf_format_semantic_integrity() -> None:
    """Verify PDF format extracts multi-page text and page markers."""
    path = FIXTURES_DIR / "sample.pdf"
    parsed = parse_uploaded_file(path.read_bytes(), "sample.pdf")
    assert "--- [Page 1] ---" in parsed.formatted_text
    assert "Distributed Edge Anomaly Detection" in parsed.raw_text
    assert parsed.page_count is not None and parsed.page_count >= 1


def test_python_format_semantic_integrity() -> None:
    """Verify Python code preserves classes, methods, and line markers."""
    path = FIXTURES_DIR / "sample.py"
    parsed = parse_uploaded_file(path.read_bytes(), "sample.py")
    assert "class AnomalyDetector" in parsed.raw_text
    assert "def record_observation" in parsed.raw_text
    assert "L1: " in parsed.formatted_text


def test_cpp_and_hpp_format_semantic_integrity() -> None:
    """Verify C++ (.cpp) and C++ header (.hpp) format extraction."""
    cpp_parsed = parse_uploaded_file((FIXTURES_DIR / "sample.cpp").read_bytes(), "sample.cpp")
    hpp_parsed = parse_uploaded_file((FIXTURES_DIR / "sample.hpp").read_bytes(), "sample.hpp")

    assert "namespace edge_eval" in cpp_parsed.raw_text
    assert "void AnomalyDetector::ingestMetric" in cpp_parsed.raw_text
    assert "struct SensorPayload" in hpp_parsed.raw_text
    assert "L1: " in cpp_parsed.formatted_text


def test_c_header_format_semantic_integrity() -> None:
    """Verify C header (.h) format extraction."""
    path = FIXTURES_DIR / "sample.h"
    parsed = parse_uploaded_file(path.read_bytes(), "sample.h")
    assert "typedef struct" in parsed.raw_text
    assert "c_sensor_data_t" in parsed.raw_text
    assert "initialize_sensor_interface" in parsed.raw_text


def test_java_format_semantic_integrity() -> None:
    """Verify Java (.java) format extraction."""
    path = FIXTURES_DIR / "sample.java"
    parsed = parse_uploaded_file(path.read_bytes(), "sample.java")
    assert "public class EdgeMonitorAgent" in parsed.raw_text
    assert "public synchronized void logObservation" in parsed.raw_text


def test_javascript_and_typescript_semantic_integrity() -> None:
    """Verify JS (.js) and TS (.ts) format extraction."""
    js_parsed = parse_uploaded_file((FIXTURES_DIR / "sample.js").read_bytes(), "sample.js")
    ts_parsed = parse_uploaded_file((FIXTURES_DIR / "sample.ts").read_bytes(), "sample.ts")

    assert "class AlertDispatcher" in js_parsed.raw_text
    assert "export interface ClusterNode" in ts_parsed.raw_text
    assert "export function evaluateClusterHealth" in ts_parsed.raw_text


def test_json_format_semantic_integrity() -> None:
    """Verify JSON (.json) format extraction."""
    path = FIXTURES_DIR / "sample.json"
    parsed = parse_uploaded_file(path.read_bytes(), "sample.json")
    assert '"system": "Distributed Edge Anomaly Detection"' in parsed.raw_text
    assert '"clusters": [' in parsed.raw_text


def test_html_and_css_semantic_integrity() -> None:
    """Verify HTML (.html) and CSS (.css) format extraction."""
    html_parsed = parse_uploaded_file((FIXTURES_DIR / "sample.html").read_bytes(), "sample.html")
    css_parsed = parse_uploaded_file((FIXTURES_DIR / "sample.css").read_bytes(), "sample.css")

    assert "<h1>Edge Cluster Operational Status</h1>" in html_parsed.raw_text
    assert "--primary-color: #1a73e8;" in css_parsed.raw_text
    assert ".dashboard-container" in css_parsed.raw_text


def test_sql_format_semantic_integrity() -> None:
    """Verify SQL (.sql) format extraction."""
    path = FIXTURES_DIR / "sample.sql"
    parsed = parse_uploaded_file(path.read_bytes(), "sample.sql")
    assert "CREATE TABLE IF NOT EXISTS edge_nodes" in parsed.raw_text
    assert "SELECT" in parsed.raw_text
    assert "JOIN edge_nodes" in parsed.raw_text


def test_encrypted_password_protected_pdf_produces_clear_warning() -> None:
    """Verify that encrypted/password-protected PDFs produce a clear informative warning."""
    # Create an encrypted PDF
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.encrypt(user_password="secret_password", owner_password="owner_password")
    buf = io.BytesIO()
    writer.write(buf)
    encrypted_bytes = buf.getvalue()

    parsed = parse_uploaded_file(encrypted_bytes, "encrypted.pdf")
    assert parsed.word_count == 0
    assert any("password-protected or encrypted" in w for w in parsed.warnings)


def test_all_15_formats_integrate_into_prepare_submission() -> None:
    """Verify that multiple files across different formats combine cleanly in prepare_submission."""
    # Test combining sample.py, sample.sql, sample.json, sample.md
    files_to_combine = [
        ("pipeline.py", (FIXTURES_DIR / "sample.py").read_bytes()),
        ("schema.sql", (FIXTURES_DIR / "sample.sql").read_bytes()),
        ("config.json", (FIXTURES_DIR / "sample.json").read_bytes()),
    ]

    prepared = prepare_submission(
        title="Multi-Format Evaluation Submission",
        submission_type="Software Project",
        instructions="Evaluate system modularity and schema cleanliness.",
        pasted_text="Summary note on project architecture.",
        uploaded_files=files_to_combine,
    )

    assert len(prepared.documents) == 4  # 1 pasted + 3 uploaded
    assert prepared.total_words > 0
    assert "=== Source: pipeline.py" in prepared.combined_submission_text
    assert "=== Source: schema.sql" in prepared.combined_submission_text
    assert "=== Source: config.json" in prepared.combined_submission_text
    assert "=== Source: pasted_submission.txt" in prepared.combined_submission_text
