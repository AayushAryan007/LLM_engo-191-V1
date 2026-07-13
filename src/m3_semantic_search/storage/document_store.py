"""In-memory document storage.

A simple, in-memory collection of documents keyed by id, with basic lookups.
It is a deliberate stand-in for a database/vector store: a later milestone (M4)
can swap it for a real vector database, but the rest of the app talks to this
same interface. No embedding logic, no search logic here.
"""

import logging

from models import Document

logger = logging.getLogger("m3_semantic_search")


class DocumentStore:
    """An in-memory store of documents keyed by id."""

    def __init__(self) -> None:
        """Initialize an empty store."""
        self._documents: dict[int, Document] = {}

    def add(self, document: Document) -> None:
        """Add or replace a single document.

        :param document: The document to store.
        """
        self._documents[document.id] = document

    def add_all(self, documents: list[Document]) -> None:
        """Add multiple documents.

        :param documents: The documents to store.
        """
        for document in documents:
            self.add(document)
        logger.info("Stored %d documents (total: %d)", len(documents), self.count())

    def all(self) -> list[Document]:
        """Return all stored documents, ordered by id.

        :returns: The stored documents.
        """
        return [self._documents[key] for key in sorted(self._documents)]

    def count(self) -> int:
        """Return the number of stored documents.

        :returns: The document count.
        """
        return len(self._documents)

    def find_by_id(self, doc_id: int) -> Document | None:
        """Return the document with the given id, or ``None`` if absent.

        :param doc_id: The id to look up.
        :returns: The matching document, or ``None``.
        """
        return self._documents.get(doc_id)

    def find_by_title(self, title: str) -> Document | None:
        """Return the first document whose title matches (case-insensitive).

        :param title: The title to look up.
        :returns: The matching document, or ``None``.
        """
        target = title.strip().lower()
        for document in self._documents.values():
            if document.title.lower() == target:
                return document
        return None
