"""Interactive terminal menus: render options and return a validated choice.

Owns menu rendering and all input validation. It never returns an invalid
selection to the caller, and it contains no AI or business logic.
"""

from utils import printer

MENU_TITLE = "Prompt Engineering Studio"

# Ordered main-menu options; the displayed number is the 1-based position.
MENU_OPTIONS: list[str] = [
    "Explain Concepts",
    "Backend Mentor",
    "SQL Assistant",
    "Code Reviewer",
    "Rewrite Text",
    "Generate Structured JSON",
    "Compare Prompt Styles",
    "Custom Playground",
    "Exit",
]


def _render(title: str, options: list[str]) -> None:
    """Print the banner and the numbered list of options."""
    printer.print_banner(title)
    for number, label in enumerate(options, start=1):
        print(f"{number}. {label}")
    print()


def choose(title: str, options: list[str]) -> int:
    """Render a titled menu and prompt until the user enters a valid option.

    :param title: The heading shown above the options.
    :param options: The selectable option labels, in display order.
    :returns: A validated 1-based option number in ``[1, len(options)]``.
    :raises KeyboardInterrupt: Propagated on Ctrl+C so the caller can exit cleanly.
    :raises EOFError: Propagated on end-of-input for the same reason.
    """
    _render(title, options)
    while True:
        raw = input("Choose an option: ").strip()

        if not raw.isdigit():
            printer.print_error("Please enter a number.")
            continue

        choice = int(raw)
        if 1 <= choice <= len(options):
            return choice

        printer.print_error(f"Choose a number between 1 and {len(options)}.")


def get_choice() -> int:
    """Render the main menu and return the validated option number.

    :returns: A validated 1-based option number for :data:`MENU_OPTIONS`.
    """
    return choose(MENU_TITLE, MENU_OPTIONS)
