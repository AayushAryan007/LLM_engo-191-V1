from config import ConfigError, require_api_key, setup_logging
from conversation import Conversation
from llm import LLMClient

EXIT_COMMANDS: set[str] = {"exit", "quit"}


def main() -> None:
    """Run the interactive terminal chat loop until the user exits."""
    logger = setup_logging()

    try:
        api_key = require_api_key()
    except ConfigError as e:
        logger.error("%s", e)
        return

    llm = LLMClient(api_key)
    conversation = Conversation()

    print("m1_cli_chat — type 'exit' or 'quit' to leave.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue
        if user_input.lower() in EXIT_COMMANDS:
            print("Goodbye.")
            break

        conversation.add_user_message(user_input)
        reply = llm.get_reply(conversation.get_messages())

        if reply is None:
            logger.warning("No reply received; message not added to history.")
            continue

        conversation.add_assistant_message(reply)
        print(f"Assistant: {reply}\n")


if __name__ == "__main__":
    main()
