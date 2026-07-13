"""Data models for the semantic search app.

Plain dataclasses only — no methods, no behavior. They describe the shapes that
flow between layers (loader -> store -> embedding -> similarity -> search).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    """A single text document loaded from the corpus.

    :param id: Stable numeric id assigned at load time.
    :param title: Human-readable title (from the document's heading or filename).
    :param content: The raw text content.
    :param source: Where the document came from (its filename).
    """

    id: int
    title: str
    content: str
    source: str


@dataclass(frozen=True)
class DocumentEmbedding:
    """A document paired with its embedding vector.

    Kept separate from :class:`Document` so raw text and its numeric
    representation can live and evolve independently.

    :param document: The source document.
    :param embedding: The embedding vector representing the document's meaning.
    """

    document: Document
    embedding: list[float]


@dataclass(frozen=True)
class SearchResult:
    """A document matched to a query, with its similarity score.

    :param document: The matched document.
    :param score: The similarity score; higher means more relevant.
    """

    document: Document
    score: float
