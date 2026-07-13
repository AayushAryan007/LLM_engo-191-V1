"""Search service: in-memory semantic search over the stored documents.

Ties the pieces together — embed the query, compare it against the cached
document embeddings using cosine similarity, filter by threshold, and return the
ranked Top-K as SearchResult objects. Document embeddings are computed once and
reused across searches. No vector database, no persistence.
"""

import logging
import time

from config import DEFAULT_TOP_K, MIN_SCORE
from models import DocumentEmbedding, SearchResult
from services.embedding_service import EmbeddingService
from similarity.cosine import cosine_similarity
from storage.document_store import DocumentStore

logger = logging.getLogger("m3_semantic_search")


class SearchService:
    """Runs semantic search over the documents in a store."""

    def __init__(self, store: DocumentStore, embeddings: EmbeddingService) -> None:
        """Store the collaborators this service orchestrates.

        :param store: The document store to search over.
        :param embeddings: The service used to embed documents and queries.
        """
        self._store = store
        self._embeddings = embeddings
        self._index: list[DocumentEmbedding] = []

    @property
    def document_count(self) -> int:
        """Number of indexed documents available to search."""
        return len(self._index)

    def index(self) -> None:
        """Embed all stored documents once and cache them for searching."""
        self._index = self._embeddings.embed_documents(self._store.all())

    def search(self, query: str, top_k: int = DEFAULT_TOP_K) -> list[SearchResult]:
        """Return the ``top_k`` documents most similar to ``query``.

        Only results scoring at least :data:`config.MIN_SCORE` are returned, so
        an empty list means "no relevant documents". Never raises for empty
        input — it returns an empty list instead.

        :param query: The search query.
        :param top_k: Maximum number of results to return.
        :returns: Matching documents with scores, most relevant first.
        """
        logger.info('Query: "%s"', query)
        start = time.perf_counter()

        if not query.strip():
            return []  # nothing to search for

        # Embed documents once (lazy), then reuse the cache on every search.
        if not self._index:
            self.index()

        query_vector = self._embeddings.embed_query(query)
        if not query_vector:
            logger.warning("Empty query embedding; returning no results.")
            return []

        results = [
            SearchResult(document=item.document, score=score)
            for item in self._index
            if (score := cosine_similarity(query_vector, item.embedding)) >= MIN_SCORE
        ]
        results.sort(key=lambda result: result.score, reverse=True)
        top_results = results[:top_k]

        elapsed_ms = round((time.perf_counter() - start) * 1000)
        logger.info("Search completed in %d ms", elapsed_ms)
        logger.info("Returned %d results", len(top_results))
        return top_results
