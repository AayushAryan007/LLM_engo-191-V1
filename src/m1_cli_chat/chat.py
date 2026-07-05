from config import require_api_key, setup_logging
from conversation import Conversation
from llm import LLMClient

EXIT_COMMANDS = {"exit", "quit"}


def main() -> None:
    logger = setup_logging()
    api_key = require_api_key(logger)

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
