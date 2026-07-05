from config import SYSTEM_PROMPT


class Conversation:
    """In-memory chat history, seeded with a system prompt."""

    def __init__(self, system_prompt: str = SYSTEM_PROMPT) -> None:
        """Initialize the conversation with a system message.

        :param system_prompt: The system prompt that steers the assistant's
            behavior. Defaults to :data:`config.SYSTEM_PROMPT`.
        """
        self.history: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]

    def add_user_message(self, content: str) -> None:
        """Append a user message to the history.

        :param content: The user's message text.
        """
        self.history.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        """Append an assistant message to the history.

        :param content: The assistant's reply text.
        """
        self.history.append({"role": "assistant", "content": content})

    def get_messages(self) -> list[dict[str, str]]:
        """Return the full conversation history.

        :returns: All messages so far, in OpenAI chat format.
        """
        return self.history
