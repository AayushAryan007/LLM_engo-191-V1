"""Search evaluation: run predefined queries and report Top-1 accuracy.

A lightweight harness (no pytest) that checks whether each query's top result
is the expected document. Run directly with ``python evaluation.py``.
"""

import logging
from dataclasses import dataclass

from bootstrap import build_search_service
from services.search_service import SearchService

logger = logging.getLogger("m3_semantic_search")


@dataclass(frozen=True)
class EvalCase:
    """One evaluation case: a query and the document expected to rank first.

    :param query: The search query.
    :param expected: The title of the document expected as the top result.
    """

    query: str
    expected: str


# Predefined cases. Queries deliberately avoid exact title keywords to test
# semantic matching rather than string matching.
EVAL_CASES: list[EvalCase] = [
    EvalCase("python language", "Python"),
    EvalCase("web api", "FastAPI"),
    EvalCase("containerization", "Docker"),
    EvalCase("cache database", "Redis"),
    EvalCase("python web framework", "Django"),
    EvalCase("asynchronous api framework", "FastAPI"),
    EvalCase("in-memory key value store", "Redis"),
    EvalCase("container image runtime", "Docker"),
    EvalCase("object relational mapper", "Django"),
    EvalCase("dynamically typed scripting language", "Python"),
]


def evaluate(search: SearchService, cases: list[EvalCase] = EVAL_CASES) -> float:
    """Run each case, print PASS/FAIL, and return accuracy as a percentage.

    :param search: A ready-to-query search service.
    :param cases: The evaluation cases to run.
    :returns: Accuracy in the range [0, 100].
    """
    passed = 0
    for case in cases:
        results = search.search(case.query, top_k=1)
        top = results[0].document.title if results else "(no result)"
        ok = top.lower() == case.expected.lower()
        passed += int(ok)

        print(f"Query      : {case.query}")
        print(f"Expected   : {case.expected}")
        print(f"Top Result : {top}")
        print(f"Result     : {'PASS' if ok else 'FAIL'}")
        print("-" * 32)

    total = len(cases)
    accuracy = (passed / total * 100) if total else 0.0

    print("Evaluation Summary")
    print(f"Queries Tested : {total}")
    print(f"Passed : {passed}")
    print(f"Accuracy : {accuracy:.0f}%")
    return accuracy


if __name__ == "__main__":
    from config import setup_logging

    setup_logging()
    evaluate(build_search_service())
