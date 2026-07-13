"""Lightweight test suite, runnable with ``python tests.py`` (no pytest).

Verifies cosine similarity, the document store, the search service, and the
evaluation module. Each test is a function that raises AssertionError on
failure; the runner reports results and exits non-zero if any test fails.
"""

import sys

from bootstrap import build_search_service
from evaluation import EVAL_CASES, evaluate
from models import Document, SearchResult
from similarity.cosine import cosine_similarity
from storage.document_store import DocumentStore

# Built once and shared across tests that need real embeddings (slow to build).
_search = None


def _search_service():
    """Lazily build and cache a real SearchService for the search/eval tests."""
    global _search
    if _search is None:
        _search = build_search_service()
    return _search


def test_cosine() -> None:
    """Cosine similarity: identical, orthogonal, zero-vector, and error cases."""
    assert cosine_similarity([1, 0], [1, 0]) == 1.0
    assert cosine_similarity([1, 0], [0, 1]) == 0.0
    assert cosine_similarity([0, 0], [1, 1]) == 0.0  # zero vector -> 0.0, no crash
    assert abs(cosine_similarity([1, 1, 0], [1, 1, 1]) - 0.8165) < 1e-3

    for a, b in (([], [1]), ([1, 2], [1])):
        try:
            cosine_similarity(a, b)
            assert False, "expected ValueError"
        except ValueError:
            pass


def test_document_store() -> None:
    """DocumentStore: add, count, and lookups by id and (case-insensitive) title."""
    store = DocumentStore()
    python = Document(1, "Python", "a", "python.txt")
    redis = Document(2, "Redis", "b", "redis.txt")
    store.add_all([python, redis])

    assert store.count() == 2
    assert store.find_by_id(1) is python
    assert store.find_by_title("redis") is redis  # case-insensitive
    assert store.find_by_id(99) is None
    assert store.find_by_title("nope") is None


def test_search_service() -> None:
    """SearchService: returns sorted SearchResults; handles empty/no-match input."""
    search = _search_service()

    results = search.search("python web framework")
    assert results, "expected at least one result"
    assert all(isinstance(r, SearchResult) for r in results)

    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True), "results must be sorted desc"
    assert all(r.score >= 0.30 for r in results), "results must clear the threshold"

    assert search.search("") == []  # empty query -> no results, no crash
    assert search.search("   ") == []  # whitespace-only -> no results


def test_evaluation() -> None:
    """Evaluation module returns a valid accuracy percentage."""
    accuracy = evaluate(_search_service(), EVAL_CASES[:3])
    assert 0.0 <= accuracy <= 100.0


TESTS = [test_cosine, test_document_store, test_search_service, test_evaluation]


def run() -> None:
    """Run every test, print a report, and exit non-zero on any failure."""
    passed = 0
    for test in TESTS:
        try:
            test()
        except AssertionError as error:
            print(f"FAIL  {test.__name__}: {error}")
        except Exception as error:  # noqa: BLE001 - report any unexpected error
            print(f"ERROR {test.__name__}: {error!r}")
        else:
            print(f"PASS  {test.__name__}")
            passed += 1

    print(f"\n{passed}/{len(TESTS)} tests passed")
    sys.exit(0 if passed == len(TESTS) else 1)


if __name__ == "__main__":
    from config import setup_logging

    setup_logging()
    run()
