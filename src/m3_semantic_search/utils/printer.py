"""Terminal output for the semantic search app.

All printing lives here. No AI, no search, no business logic — callers describe
what to show, this module owns how it looks.
"""

from models import Document, SearchResult

_WIDTH = 50
_RULE = "-" * 40


def print_rule() -> None:
    """Print a horizontal rule separating sections."""
    print(_RULE)


def print_section(title: str, lines: list[str]) -> None:
    """Print a titled section framed by a leading rule.

    :param title: The section heading.
    :param lines: The content lines to print under the heading.
    """
    print(_RULE)
    print(title)
    print()
    for line in lines:
        print(line)


def print_banner(title: str) -> None:
    """Print a centered title framed by a horizontal rule.

    :param title: The heading text.
    """
    line = "=" * _WIDTH
    print(f"\n{line}\n{title.center(_WIDTH)}\n{line}")


def print_message(text: str) -> None:
    """Print a plain message.

    :param text: The text to display.
    """
    print(text)


def print_error(text: str) -> None:
    """Print an error message.

    :param text: The error description.
    """
    print(f"[error] {text}")


def print_documents(documents: list[Document]) -> None:
    """Print a one-line summary for each loaded document.

    :param documents: The documents to summarize.
    """
    for document in documents:
        print(f"- {document.title} ({len(document.content)} chars)")


def print_results(results: list[SearchResult]) -> None:
    """Print ranked search results as a titled section.

    :param results: The results to display, already ordered best-first.
    """
    lines = [
        f"{rank}. {result.document.title}  (similarity: {result.score:.2f})"
        for rank, result in enumerate(results, start=1)
    ]
    print_section("Top Results", lines)
    print_rule()
