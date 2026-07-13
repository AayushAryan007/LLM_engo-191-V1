"""Embedding service: turn Document objects into DocumentEmbedding objects.

Business logic only — it orchestrates the client but never talks to the
provider directly, so swapping the client implementation leaves this file
unchanged. No searching, no cosine similarity, no ranking.
"""

import logging
import time

from embedding_client import EmbeddingClient
from models import Document, DocumentEmbedding

logger = logging.getLogger("m3_semantic_search")


class EmbeddingService:
    """Generates embeddings for documents via an injected EmbeddingClient."""

    def __init__(self, client: EmbeddingClient) -> None:
        """Store the embedding client dependency.

        :param client: The client used to produce embedding vectors.
        """
        self._client = client

    def embed_document(self, document: Document) -> DocumentEmbedding:
        """Embed a single document.

        :param document: The document to embed.
        :returns: The document paired with its embedding vector.
        """
        vector = self._client.embed(document.content)
        return DocumentEmbedding(document=document, embedding=vector)

    def embed_query(self, query: str) -> list[float]:
        """Embed a search query into the same vector space as the documents.

        :param query: The query text.
        :returns: The query's embedding vector.
        """
        return self._client.embed(query)

    def embed_documents(self, documents: list[Document]) -> list[DocumentEmbedding]:
        """Embed multiple documents, logging count, dimension, and elapsed time.

        :param documents: The documents to embed.
        :returns: One :class:`DocumentEmbedding` per input document.
        """
        start = time.perf_counter()
        embeddings = [self.embed_document(document) for document in documents]
        elapsed = time.perf_counter() - start

        dimension = len(embeddings[0].embedding) if embeddings else 0
        logger.info(
            "Embedded %d documents (dimension=%d) in %.2fs",
            len(embeddings),
            dimension,
            elapsed,
        )
        return embeddings
