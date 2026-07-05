"""Application entry point and orchestrator.

Wires configuration, the LLM client, and services together, then runs the
menu loop. It holds no business logic, no API calls, and no prompt logic:
it only coordinates the other layers.
"""

from config import ConfigError, get_settings, setup_logging
from llm import LLMClient
from services.playground_service import PlaygroundService
from utils import menu, printer

PLAYGROUND_OPTION = 8
EXIT_OPTION = 9


def _run_playground(service: PlaygroundService) -> None:
    """Read one message, hand it to the service, and display the reply.

    :param service: The playground service that owns the exchange logic.
    """
    user_input = input("Your message: ").strip()
    if not user_input:
        printer.print_error("Message cannot be empty.")
        return

    reply = service.run(user_input)
    if reply is None:
        printer.print_error("No reply received. See the log above for details.")
        return

    printer.print_message(reply)


def main() -> None:
    """Initialize dependencies and run the menu loop until the user exits."""
    logger = setup_logging()

    try:
        settings = get_settings()
    except ConfigError as e:
        printer.print_error(str(e))
        return

    llm = LLMClient(settings)
    playground = PlaygroundService(llm)
    logger.info("Prompt Studio started (model=%s)", settings.model)

    try:
        while True:
            choice = menu.get_choice()

            if choice == EXIT_OPTION:
                printer.print_success("Goodbye.")
                break
            if choice == PLAYGROUND_OPTION:
                _run_playground(playground)
            else:
                printer.print_message("Coming in Phase 2")
    except (KeyboardInterrupt, EOFError):
        printer.print_success("Goodbye.")


if __name__ == "__main__":
    main()
