"""Application configuration: logging and project constants.

Phase 1 has no AI and no API calls, so there is no API key or Settings object
yet. This module centralizes logging setup and the paths/constants the rest of
the app depends on.
"""

import logging
from pathlib import Path

# Absolute path to the bundled corpus, resolved relative to this file so the
# app works regardless of the current working directory.
DOCUMENTS_DIR: Path = Path(__file__).parent / "documents"

# Embedding model used to turn text into vectors.
EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

# Semantic search tuning.
DEFAULT_TOP_K: int = 3  # how many results to return by default
MIN_SCORE: float = 0.30  # ignore matches weaker than this cosine score


def setup_logging() -> logging.Logger:
    """Configure application-wide logging and return the app logger.

    :returns: The ``m3_semantic_search`` logger, ready for use by callers.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("m3_semantic_search")
