"""Embedding client: turns text into vectors.

The abstraction (:class:`EmbeddingClient`) is what the rest of the app depends
on; the concrete implementation is swappable. Today it wraps a local
sentence-transformers model, so embeddings run offline with no API key. A future
OpenAI-compatible client can implement the same interface without changing
EmbeddingService or anything above it — this file is the only place that knows
which provider is used.
"""

import logging
from abc import ABC, abstractmethod

from config import EMBEDDING_MODEL

logger = logging.getLogger("m3_semantic_search")


class EmbeddingClient(ABC):
    """Interface for anything that turns text into an embedding vector."""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Return the embedding vector for ``text``.

        :param text: The input text to embed.
        :returns: The embedding as a list of floats.
        """

    @property
    @abstractmethod
    def dimension(self) -> int:
        """The length of the vectors this client produces."""


class SentenceTransformerEmbeddingClient(EmbeddingClient):
    """EmbeddingClient backed by a local sentence-transformers model."""

    def __init__(self, model: str = EMBEDDING_MODEL) -> None:
        """Load the embedding model.

        :param model: The sentence-transformers model identifier.
        """
        # Imported lazily so the heavy dependency loads only when embeddings are
        # actually used, and other modules can import this file cheaply.
        from sentence_transformers import SentenceTransformer

        logger.info("Loading embedding model: %s", model)
        self._model = SentenceTransformer(model)

    def embed(self, text: str) -> list[float]:
        """Return the embedding vector for ``text``.

        :param text: The input text to embed.
        :returns: The embedding as a list of floats.
        """
        vector = self._model.encode(text)
        return vector.tolist()

    @property
    def dimension(self) -> int:
        """The embedding dimension of the loaded model."""
        return self._model.get_embedding_dimension()
