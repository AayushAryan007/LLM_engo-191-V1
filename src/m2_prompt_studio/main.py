"""Application entry point and orchestrator.

Wires configuration, the LLM client, and services together, then runs the
menu loop. It holds no business logic, no API calls, and no prompt logic:
it only coordinates the other layers.
"""

from config import AVAILABLE_MODELS, ConfigError, get_settings, setup_logging
from llm import LLMClient
from services.backend_service import TOPICS, BackendMentorService
from services.explain_service import Audience, ExplainService
from services.playground_service import PlaygroundService
from services.compare_service import CompareService
from services.json_service import JSONService
from services.review_service import ReviewMode, ReviewService
from services.rewrite_service import RewriteService, RewriteStyle
from services.sql_service import Capability, SQLAssistantService
from utils import menu, printer

EXPLAIN_OPTION = 1
MENTOR_OPTION = 2
SQL_OPTION = 3
REVIEW_OPTION = 4
REWRITE_OPTION = 5
JSON_OPTION = 6
COMPARE_OPTION = 7
PLAYGROUND_OPTION = 8
EXIT_OPTION = 9


def _print_reply(reply: str | None) -> None:
    """Display a service reply, or an error if the call failed.

    :param reply: The service's return value (text, or ``None`` on failure).
    """
    if reply is None:
        printer.print_error("No reply received. See the log above for details.")
        return
    printer.print_message(reply)


_PLAYGROUND_ACTIONS = [
    "Send a message",
    "View settings",
    "Set system prompt",
    "Set temperature",
    "Set max tokens",
    "Select model",
    "Toggle history",
    "Clear history",
    "Back to main menu",
]


def _run_playground(service: PlaygroundService, models: list[str]) -> None:
    """Run the interactive playground sub-loop until the user goes back.

    :param service: The stateful playground service.
    :param models: Selectable model ids for the model picker.
    """
    while True:
        action = menu.choose("Playground", _PLAYGROUND_ACTIONS)

        if action == 1:  # Send a message
            message = input("You: ").strip()
            if not message:
                printer.print_error("Message cannot be empty.")
                continue
            _print_reply(service.send(message))
        elif action == 2:  # View settings
            summary = "\n".join(
                f"{name}: {value}" for name, value in service.current_settings().items()
            )
            printer.print_message(summary)
        elif action == 3:  # Set system prompt
            prompt = input("System prompt: ").strip()
            if not prompt:
                printer.print_error("System prompt cannot be empty.")
                continue
            service.set_system_prompt(prompt)
            printer.print_success("System prompt updated.")
        elif action == 4:  # Set temperature
            raw = input("Temperature (0.0-2.0): ").strip()
            try:
                temperature = float(raw)
            except ValueError:
                printer.print_error("Temperature must be a number.")
                continue
            if not 0.0 <= temperature <= 2.0:
                printer.print_error("Temperature must be between 0.0 and 2.0.")
                continue
            service.set_temperature(temperature)
            printer.print_success(f"Temperature set to {temperature}.")
        elif action == 5:  # Set max tokens
            raw = input("Max tokens: ").strip()
            if not raw.isdigit() or int(raw) == 0:
                printer.print_error("Max tokens must be a positive integer.")
                continue
            service.set_max_tokens(int(raw))
            printer.print_success(f"Max tokens set to {raw}.")
        elif action == 6:  # Select model
            choice = menu.choose("Select Model", models)
            model = models[choice - 1]
            service.set_model(model)
            printer.print_success(f"Model set to {model}.")
        elif action == 7:  # Toggle history
            enabled = service.toggle_history()
            printer.print_success(f"History {'enabled' if enabled else 'disabled'}.")
        elif action == 8:  # Clear history
            service.clear_history()
            printer.print_success("Conversation history cleared.")
        else:  # Back to main menu
            return


def _run_explain(service: ExplainService) -> None:
    """Read a topic and audience, then display the tailored explanation.

    :param service: The explain service that owns the prompt/message logic.
    """
    topic = input("Enter Topic: ").strip()
    if not topic:
        printer.print_error("Topic cannot be empty.")
        return

    choice = menu.choose("Choose Audience", Audience.labels())
    audience = Audience.from_choice(choice)
    _print_reply(service.run(topic, audience))


def _run_mentor(service: BackendMentorService) -> None:
    """Read a topic choice, then display the mentor's guidance.

    :param service: The backend mentor service that owns the prompt/message logic.
    """
    choice = menu.choose("Backend Mentor", TOPICS)
    topic = TOPICS[choice - 1]
    _print_reply(service.run(topic))


def _run_sql(service: SQLAssistantService) -> None:
    """Read a SQL query and a capability, then display the result.

    :param service: The SQL assistant service that owns the prompt/message logic.
    """
    sql = input("Enter SQL: ").strip()
    if not sql:
        printer.print_error("SQL cannot be empty.")
        return

    choice = menu.choose("SQL Assistant", Capability.labels())
    capability = Capability.from_choice(choice)
    _print_reply(service.run(sql, capability))


def _run_review(service: ReviewService) -> None:
    """Read code and a review mode, then display the review.

    :param service: The review service that owns the prompt/message logic.
    """
    code = input("Paste code: ").strip()
    if not code:
        printer.print_error("Code cannot be empty.")
        return

    choice = menu.choose("Code Reviewer", ReviewMode.labels())
    mode = ReviewMode.from_choice(choice)
    _print_reply(service.run(code, mode))


def _run_rewrite(service: RewriteService) -> None:
    """Read text and a rewrite style, then display the rewritten text.

    :param service: The rewrite service that owns the prompt/message logic.
    """
    text = input("Enter text: ").strip()
    if not text:
        printer.print_error("Text cannot be empty.")
        return

    choice = menu.choose("Rewrite Assistant", RewriteStyle.labels())
    style = RewriteStyle.from_choice(choice)
    _print_reply(service.run(text, style))


def _run_json(service: JSONService) -> None:
    """Read a request, generate JSON, and display it (or a validation error).

    :param service: The JSON service that owns generation and validation.
    """
    request = input("Describe the JSON you want: ").strip()
    if not request:
        printer.print_error("Request cannot be empty.")
        return

    result = service.run(request)
    if result.ok:
        printer.print_message(result.content)
    else:
        printer.print_error(result.content)


def _run_compare(service: CompareService) -> None:
    """Read a question, run it through every strategy, and display each answer.

    :param service: The comparison service that owns the multi-strategy logic.
    """
    question = input("Enter question: ").strip()
    if not question:
        printer.print_error("Question cannot be empty.")
        return

    for label, answer in service.run(question):
        printer.print_banner(label)
        if answer is None:
            printer.print_error("No reply for this strategy.")
        else:
            printer.print_message(answer)


def main() -> None:
    """Initialize dependencies and run the menu loop until the user exits."""
    logger = setup_logging()

    try:
        settings = get_settings()
    except ConfigError as e:
        printer.print_error(str(e))
        return

    llm = LLMClient(settings)
    explain = ExplainService(llm)
    mentor = BackendMentorService(llm)
    sql = SQLAssistantService(llm)
    review = ReviewService(llm)
    rewrite = RewriteService(llm)
    json_gen = JSONService(llm)
    compare = CompareService(llm)
    playground = PlaygroundService(llm, settings.model)
    logger.info("Prompt Studio started (model=%s)", settings.model)

    try:
        while True:
            choice = menu.get_choice()

            if choice == EXIT_OPTION:
                printer.print_success("Goodbye.")
                break
            if choice == EXPLAIN_OPTION:
                _run_explain(explain)
            elif choice == MENTOR_OPTION:
                _run_mentor(mentor)
            elif choice == SQL_OPTION:
                _run_sql(sql)
            elif choice == REVIEW_OPTION:
                _run_review(review)
            elif choice == REWRITE_OPTION:
                _run_rewrite(rewrite)
            elif choice == JSON_OPTION:
                _run_json(json_gen)
            elif choice == COMPARE_OPTION:
                _run_compare(compare)
            elif choice == PLAYGROUND_OPTION:
                _run_playground(playground, AVAILABLE_MODELS)
            else:
                printer.print_message("Coming in a future sprint.")
    except (KeyboardInterrupt, EOFError):
        printer.print_success("Goodbye.")


if __name__ == "__main__":
    main()
