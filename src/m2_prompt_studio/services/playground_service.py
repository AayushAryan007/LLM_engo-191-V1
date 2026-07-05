"""Playground service: business logic for the free-form chat module.

Turns a user's raw message into chat messages, calls the LLM, and returns the
reply. It knows nothing about menus or terminal formatting.
"""

import logging

from llm import LLMClient, Message

logger = logging.getLogger("m2_prompt_studio")


class PlaygroundService:
    """Handles a single free-form playground exchange."""

    def __init__(self, llm: LLMClient) -> None:
        """Initialize the service with an LLM client.

        :param llm: The client used to send messages to the model.
        """
        self._llm = llm

    def run(self, user_input: str) -> str | None:
        """Turn the user's input into messages, call the LLM, and return the reply.

        :param user_input: The raw message typed by the user.
        :returns: The assistant's reply text, or ``None`` if the request failed.
        """
        messages = self._build_messages(user_input)
        logger.info("Playground request (%d chars)", len(user_input))
        return self._llm.get_reply(messages)

    def _build_messages(self, user_input: str) -> list[Message]:
        """Wrap raw user input as chat messages.

        Phase 1 sends the message as-is with no system prompt. Prompt
        engineering (system prompts, few-shot examples) plugs in here in Phase 2.

        :param user_input: The raw message typed by the user.
        :returns: Chat messages ready for the LLM client.
        """
        return [{"role": "user", "content": user_input}]
