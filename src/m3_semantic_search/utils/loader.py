"""Corpus loader: reads the bundled .txt documents into Document models.

This is the only place that touches the filesystem for the corpus. It returns
plain data (list[Document]) and does no storage, embedding, or printing.
"""

import logging

from config import DOCUMENTS_DIR
from models import Document

logger = logging.getLogger("m3_semantic_search")


def _derive_title(content: str, fallback: str) -> str:
    """Use the first Markdown H1 heading as the title, else the filename.

    :param content: The document text.
    :param fallback: A name to use when no heading is present.
    :returns: A human-readable title.
    """
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback.replace("_", " ").title()


def load_documents() -> list[Document]:
    """Load every ``.txt`` file in the documents directory.

    Non-text files are ignored (only ``*.txt`` is read). Ids are assigned in
    sorted-filename order so they are stable across runs.

    :returns: One :class:`Document` per text file.
    :raises FileNotFoundError: If the documents directory does not exist.
    """
    if not DOCUMENTS_DIR.is_dir():
        raise FileNotFoundError(f"Documents directory not found: {DOCUMENTS_DIR}")

    documents: list[Document] = []
    for doc_id, path in enumerate(sorted(DOCUMENTS_DIR.glob("*.txt")), start=1):
        content = path.read_text(encoding="utf-8").strip()
        documents.append(
            Document(
                id=doc_id,
                title=_derive_title(content, path.stem),
                content=content,
                source=path.name,
            )
        )

    logger.info("Loaded %d documents from %s", len(documents), DOCUMENTS_DIR)
    return documents
