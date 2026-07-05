"""Terminal output formatting.

Every ``print`` in the application lives here. Other modules describe *what*
to show; this module owns *how* it looks. It contains no AI or business logic.
"""

_WIDTH = 45


def print_banner(title: str) -> None:
    """Print a centered title framed by a horizontal rule.

    :param title: The text to display as the banner heading.
    """
    line = "=" * _WIDTH
    print(f"\n{line}\n{title.center(_WIDTH)}\n{line}")


def print_message(text: str) -> None:
    """Print an assistant/response message.

    :param text: The message body to display.
    """
    print(f"\n{text}\n")


def print_error(text: str) -> None:
    """Print an error message for the user.

    :param text: The error description to display.
    """
    print(f"[error] {text}")


def print_success(text: str) -> None:
    """Print a success/confirmation message.

    :param text: The message to display.
    """
    print(f"[ok] {text}")
