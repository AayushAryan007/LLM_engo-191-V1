"""Interactive terminal menu: render options and return a validated choice.

Owns the menu's option list and all input validation. It never returns an
invalid selection to the caller, and it contains no AI or business logic.
"""

from utils import printer

MENU_TITLE = "Prompt Engineering Studio"

# Ordered menu options; the displayed number is the 1-based position.
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


def _render() -> None:
    """Print the banner and the numbered list of options."""
    printer.print_banner(MENU_TITLE)
    for number, label in enumerate(MENU_OPTIONS, start=1):
        print(f"{number}. {label}")
    print()


def get_choice() -> int:
    """Render the menu and prompt until the user enters a valid option.

    :returns: A validated 1-based option number in ``[1, len(MENU_OPTIONS)]``.
    :raises KeyboardInterrupt: Propagated on Ctrl+C so the caller can exit cleanly.
    :raises EOFError: Propagated on end-of-input for the same reason.
    """
    _render()
    while True:
        raw = input("Choose an option: ").strip()

        if not raw.isdigit():
            printer.print_error("Please enter a number.")
            continue

        choice = int(raw)
        if 1 <= choice <= len(MENU_OPTIONS):
            return choice

        printer.print_error(f"Choose a number between 1 and {len(MENU_OPTIONS)}.")
