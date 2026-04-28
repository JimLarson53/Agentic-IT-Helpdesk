"""Document loading for sanitized local corpora."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

from itsupport_copilot.schemas.rag import (
    DocumentMetadata,
    DocumentType,
    LoadedDocument,
    Sensitivity,
)

SUPPORTED_TEXT_EXTENSIONS = {".md", ".txt", ".rst"}


def infer_document_type(path: Path) -> DocumentType:
    """Infer document type from folder and filename hints."""

    hints = " ".join(part.lower() for part in (*path.parts, path.stem))
    if "resume" in hints:
        return DocumentType.RESUME
    if "job" in hints and "description" in hints:
        return DocumentType.JOB_DESCRIPTION
    if "kb" in hints or "knowledge" in hints:
        return DocumentType.KB_ARTICLE
    if "troubleshooting" in hints or "troubleshoot" in hints:
        return DocumentType.TROUBLESHOOTING_NOTE
    if "ticket" in hints:
        return DocumentType.SAMPLE_TICKET
    if "security" in hints:
        return DocumentType.SECURITY_NOTE
    if "doc" in hints or "runbook" in hints or "policy" in hints:
        return DocumentType.IT_DOCUMENTATION
    return DocumentType.UNKNOWN


def extract_title(content: str, fallback: str) -> str:
    """Extract a readable title from Markdown or plain text."""

    for line in content.splitlines():
        clean = line.strip().lstrip("#").strip()
        if clean:
            return clean[:120]
    return fallback


def compute_source_id(filename: str, content: str) -> str:
    """Create a stable source ID that does not depend on local absolute paths."""

    digest = hashlib.sha256(f"{filename}\n{content}".encode("utf-8")).hexdigest()
    return digest[:20]


def _read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def load_text_document(
    path: str | Path,
    *,
    document_type: DocumentType | None = None,
    sensitivity: Sensitivity = Sensitivity.INTERNAL,
    tags: Iterable[str] | None = None,
) -> LoadedDocument:
    """Load a supported text document with metadata."""

    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Document not found: {file_path}")
    if file_path.suffix.lower() not in SUPPORTED_TEXT_EXTENSIONS:
        raise ValueError(f"Unsupported document extension: {file_path.suffix}")

    content = _read_text(file_path).strip()
    inferred_type = document_type or infer_document_type(file_path)
    metadata = DocumentMetadata(
        source_id=compute_source_id(file_path.name, content),
        source_path=str(file_path),
        filename=file_path.name,
        document_type=inferred_type,
        sensitivity=sensitivity,
        title=extract_title(content, file_path.stem),
        tags=sorted(set(tags or [])),
    )
    return LoadedDocument(metadata=metadata, content=content)


def load_documents_from_directory(
    root: str | Path,
    *,
    sensitivity: Sensitivity = Sensitivity.INTERNAL,
    tags: Iterable[str] | None = None,
) -> list[LoadedDocument]:
    """Recursively load supported text documents from a directory."""

    root_path = Path(root)
    if not root_path.is_dir():
        raise NotADirectoryError(f"Corpus directory not found: {root_path}")

    documents: list[LoadedDocument] = []
    for path in sorted(root_path.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_TEXT_EXTENSIONS:
            documents.append(load_text_document(path, sensitivity=sensitivity, tags=tags))
    return documents
