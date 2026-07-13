"""Application entry point for m3_semantic_search (interactive semantic search).

Orchestrates only: build the search index, then run an interactive search loop.
All business logic lives in the services; all output lives in the printer.
"""

from bootstrap import build_search_service
from config import setup_logging
from utils import printer

EXIT_COMMANDS = {"exit", "quit"}


def main() -> None:
    """Build the search index, then serve interactive searches."""
    logger = setup_logging()

    search = build_search_service()
    if search.document_count == 0:
        printer.print_message("No documents available to search.")
        return

    printer.print_section(
        "Semantic Search",
        [f"Loaded {search.document_count} documents.", "Type a query, or 'exit' to quit."],
    )

    while True:
        try:
            query = input("\nSearch > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if query.lower() in EXIT_COMMANDS:
            break
        if not query:
            printer.print_message("Please enter a search query.")
            continue

        results = search.search(query)
        if not results:
            printer.print_message("No relevant documents found.")
            continue
        printer.print_results(results)

    printer.print_message("Goodbye.")
    logger.info("Search session ended.")


if __name__ == "__main__":
    main()
