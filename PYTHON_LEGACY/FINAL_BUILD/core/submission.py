"""
Submission Processing and Aggregation for EvalLens.

Coordinates document parsing, combines pasted text with multi-file uploads,
validates the 5,000-word submission limit, and persists submission records to SQLite.
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from config.settings import settings
from core.document_parser import (
    MAX_SUBMISSION_WORDS,
    ParsedDocument,
    check_submission_word_limit,
    parse_text_content,
    parse_uploaded_file,
)
from database.db import add_submission, create_evaluation


def suggest_evaluation_title(filename: str, text: str = "") -> str:
    """Suggest a user-facing evaluation name from a document heading or filename."""
    for raw_line in text.splitlines():
        line = raw_line.strip().lstrip("#").strip()
        if line.startswith("<title>") and line.endswith("</title>"):
            line = line[7:-8].strip()
        if line and not line.startswith(("---", "===", "L1:")):
            return line[:120]
    return Path(filename).stem or "Untitled Evaluation"


@dataclass
class PreparedSubmission:
    """Represents a validated, aggregated submission ready for evaluation."""

    title: str
    submission_type: str
    instructions: Optional[str]
    reference_material: Optional[str]
    prompt_version: str
    documents: List[ParsedDocument]
    total_words: int
    combined_submission_text: str
    warnings: List[str] = field(default_factory=list)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal or invalid characters."""
    base_name = Path(filename).name
    clean = re.sub(r"[^\w\.-]", "_", base_name)
    clean = clean.lstrip(".")
    return clean or "unnamed_file"


def prepare_submission(
    title: str,
    submission_type: str = "Custom",
    instructions: Optional[str] = None,
    reference_material: Optional[str] = None,
    pasted_text: Optional[str] = None,
    uploaded_files: Optional[List[Tuple[str, bytes]]] = None,
    prompt_version: str = "V3",
) -> PreparedSubmission:
    """
    Parse and validate text input and all uploaded files.
    Enforces the combined 5,000-word limit. Disambiguates duplicate filenames.
    """
    title_clean = title.strip()
    if not title_clean:
        raise ValueError("Evaluation title is required.")

    parsed_docs: List[ParsedDocument] = []
    all_warnings: List[str] = []

    # 1. Parse pasted text if provided
    if pasted_text and pasted_text.strip():
        parsed_pasted = parse_text_content(
            pasted_text.strip(), filename="pasted_submission.txt", is_code=False
        )
        parsed_docs.append(parsed_pasted)
        all_warnings.extend(parsed_pasted.warnings)

    # 2. Parse uploaded files with duplicate name disambiguation
    if uploaded_files:
        seen_names: Dict[str, int] = {}
        for fname, fbytes in uploaded_files:
            clean_name = sanitize_filename(fname)
            if clean_name in seen_names:
                seen_names[clean_name] += 1
                p = Path(clean_name)
                unique_name = f"{p.stem}_{seen_names[clean_name]}{p.suffix}"
            else:
                seen_names[clean_name] = 1
                unique_name = clean_name

            parsed_doc = parse_uploaded_file(fbytes, unique_name)
            parsed_docs.append(parsed_doc)
            all_warnings.extend(parsed_doc.warnings)

    # 3. Check for empty submission
    if not parsed_docs:
        raise ValueError("Please provide at least one text submission or upload a supported file.")

    # 4. Calculate total words across all parsed documents
    # Note: reference material is intentionally separate and not counted in submission limit
    total_words = sum(doc.word_count for doc in parsed_docs)

    # 5. Check if total text exceeds 5,000 words
    is_valid_words, word_msg = check_submission_word_limit(total_words)
    if not is_valid_words:
        raise ValueError(word_msg)

    # Combine text for evaluation reference
    text_sections: List[str] = []
    for doc in parsed_docs:
        header = f"=== Source: {doc.filename} ({doc.word_count:,} words) ==="
        text_sections.append(f"{header}\n{doc.formatted_text}")

    combined_text = "\n\n".join(text_sections)

    return PreparedSubmission(
        title=title_clean,
        submission_type=submission_type,
        instructions=instructions.strip() if instructions and instructions.strip() else None,
        reference_material=reference_material.strip() if reference_material and reference_material.strip() else None,
        prompt_version=prompt_version,
        documents=parsed_docs,
        total_words=total_words,
        combined_submission_text=combined_text,
        warnings=all_warnings,
    )


def save_submission_to_db(
    prepared: PreparedSubmission,
    uploaded_files_data: Optional[List[Tuple[str, bytes]]] = None,
    db_path: Optional[Path] = None,
) -> int:
    """
    Save the evaluation and its constituent submissions into the SQLite database.
    Saves uploaded files to the uploads/ directory.
    Returns the newly created evaluation_id.
    """
    # 1. Create evaluation record
    eval_id = create_evaluation(
        title=prepared.title,
        description=f"Type: {prepared.submission_type} | Words: {prepared.total_words:,}",
        submission_type=prepared.submission_type,
        instructions=prepared.instructions,
        reference_material=prepared.reference_material,
        prompt_version=prepared.prompt_version,
        total_words=prepared.total_words,
        status="draft",
        db_path=db_path,
    )

    # Map filename to file_bytes if provided, matching duplicate disambiguation
    file_bytes_map: Dict[str, bytes] = {}
    if uploaded_files_data:
        seen_names: Dict[str, int] = {}
        for fname, fbytes in uploaded_files_data:
            clean_name = sanitize_filename(fname)
            if clean_name in seen_names:
                seen_names[clean_name] += 1
                p = Path(clean_name)
                unique_name = f"{p.stem}_{seen_names[clean_name]}{p.suffix}"
            else:
                seen_names[clean_name] = 1
                unique_name = clean_name
            file_bytes_map[unique_name] = fbytes

    # 2. Save each parsed document as a submission row
    for doc in prepared.documents:
        saved_file_path = ""
        if doc.filename in file_bytes_map:
            # Save file to uploads/
            safe_name = sanitize_filename(doc.filename)
            unique_filename = f"{eval_id}_{uuid.uuid4().hex[:8]}_{safe_name}"
            target_uploads_dir = settings.uploads_dir
            dest_path = (target_uploads_dir / unique_filename).resolve()
            
            # Security verification: path traversal prevention
            if not str(dest_path).startswith(str(target_uploads_dir.resolve())):
                raise ValueError(f"Security error: path traversal outside uploads dir detected for '{doc.filename}'.")

            try:
                with open(dest_path, "wb") as f:
                    f.write(file_bytes_map[doc.filename])
                saved_file_path = str(dest_path)
            except Exception as e:
                prepared.warnings.append(f"Failed to persist file {doc.filename} to disk: {e}")

        warnings_str = "; ".join(doc.warnings) if doc.warnings else ""

        add_submission(
            evaluation_id=eval_id,
            title=doc.filename,
            content=doc.formatted_text,
            file_name=doc.filename,
            file_path=saved_file_path,
            file_type=doc.extension,
            word_count=doc.word_count,
            warnings=warnings_str,
            db_path=db_path,
        )

    return eval_id
