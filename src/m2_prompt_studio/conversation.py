"""Conversation state for the Playground.

Owns the system prompt and the running list of user/assistant turns, and knows
how to assemble the messages for the next call (with or without prior history).
It performs no I/O and never calls the LLM.
"""

from llm import Message

DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."


class Conversation:
    """Holds the system prompt and the turn history of a playground chat."""

    def __init__(self, system_prompt: str = DEFAULT_SYSTEM_PROMPT) -> None:
        """Initialize with a system prompt and an empty history.

        :param system_prompt: The initial system prompt.
        """
        self._system_prompt = system_prompt
        self._turns: list[Message] = []

    @property
    def system_prompt(self) -> str:
        """The current system prompt."""
        return self._system_prompt

    @property
    def exchange_count(self) -> int:
        """Number of completed user/assistant exchanges."""
        return len(self._turns) // 2

    def set_system_prompt(self, prompt: str) -> None:
        """Replace the system prompt (does not clear history).

        :param prompt: The new system prompt.
        """
        self._system_prompt = prompt

    def record_exchange(self, user_input: str, assistant_reply: str) -> None:
        """Append a completed user/assistant exchange to the history.

        :param user_input: The user's message.
        :param assistant_reply: The assistant's reply.
        """
        self._turns.append({"role": "user", "content": user_input})
        self._turns.append({"role": "assistant", "content": assistant_reply})

    def clear(self) -> None:
        """Remove all recorded turns (keeps the system prompt)."""
        self._turns.clear()

    def build_messages(self, user_input: str, include_history: bool) -> list[Message]:
        """Assemble the messages for the next call.

        :param user_input: The new user message.
        :param include_history: If True, include prior turns; if False, send
            only the system prompt and the new user message.
        :returns: Chat messages ready for the LLM client.
        """
        history = self._turns if include_history else []
        return [
            {"role": "system", "content": self._system_prompt},
            *history,
            {"role": "user", "content": user_input},
        ]
