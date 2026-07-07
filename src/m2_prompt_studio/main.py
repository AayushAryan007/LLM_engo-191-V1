"""Application entry point and orchestrator.

Wires configuration, the LLM client, and services together, then runs the
menu loop. It holds no business logic, no API calls, and no prompt logic:
it only coordinates the other layers.
"""

from config import ConfigError, get_settings, setup_logging
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


def _run_playground(service: PlaygroundService) -> None:
    """Read one message, hand it to the service, and display the reply.

    :param service: The playground service that owns the exchange logic.
    """
    user_input = input("Your message: ").strip()
    if not user_input:
        printer.print_error("Message cannot be empty.")
        return
    _print_reply(service.run(user_input))


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
    playground = PlaygroundService(llm)
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
                _run_playground(playground)
            else:
                printer.print_message("Coming in a future sprint.")
    except (KeyboardInterrupt, EOFError):
        printer.print_success("Goodbye.")


if __name__ == "__main__":
    main()
