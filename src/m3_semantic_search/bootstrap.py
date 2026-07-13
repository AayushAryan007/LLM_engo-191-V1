"""Application bootstrap: build a ready-to-use SearchService.

A single place that wires the corpus, store, embedding client/service, and
search service together, so main, evaluation, and tests share one setup path
instead of duplicating it.
"""

import logging

from embedding_client import SentenceTransformerEmbeddingClient
from services.embedding_service import EmbeddingService
from services.search_service import SearchService
from storage.document_store import DocumentStore
from utils import loader

logger = logging.getLogger("m3_semantic_search")


def build_search_service() -> SearchService:
    """Load and index the corpus, returning a ready-to-query SearchService.

    :returns: A SearchService whose document embeddings are already built.
    :raises FileNotFoundError: If the documents directory is missing.
    """
    documents = loader.load_documents()
    if not documents:
        logger.warning("No documents loaded; search will return no results.")

    store = DocumentStore()
    store.add_all(documents)

    embeddings = EmbeddingService(SentenceTransformerEmbeddingClient())
    search = SearchService(store, embeddings)
    search.index()
    return search
