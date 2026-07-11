"""Playground service: stateful, configurable free-form chat.

Owns the conversation state (via Conversation) and the runtime settings
(history toggle, temperature, max tokens, model). It forwards those settings to
llm.py but never talks to Groq itself. No I/O, no printing.
"""

import logging

from conversation import Conversation
from llm import LLMClient

logger = logging.getLogger("m2_prompt_studio")


class PlaygroundService:
    """A stateful chat playground with adjustable model settings."""

    def __init__(self, llm: LLMClient, model: str) -> None:
        """Initialize with an LLM client and the default model.

        :param llm: The client used to send messages to the model.
        :param model: The initial model id (from application settings).
        """
        self._llm = llm
        self._conversation = Conversation()
        self._history_enabled = True
        self._temperature: float | None = None
        self._max_tokens: int | None = None
        self._model = model

    def send(self, user_input: str) -> str | None:
        """Send a message and return the reply, recording it only on success.

        :param user_input: The user's message.
        :returns: The assistant's reply, or ``None`` if the request failed.
        """
        messages = self._conversation.build_messages(user_input, self._history_enabled)
        logger.info(
            "Playground send (model=%s, history=%s, temp=%s, max_tokens=%s)",
            self._model,
            self._history_enabled,
            self._temperature,
            self._max_tokens,
        )
        reply = self._llm.get_reply(
            messages,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            model=self._model,
        )
        if reply is None:
            return None
        self._conversation.record_exchange(user_input, reply)
        return reply

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self._conversation.clear()

    def toggle_history(self) -> bool:
        """Toggle whether prior turns are sent.

        :returns: The new history-enabled state.
        """
        self._history_enabled = not self._history_enabled
        return self._history_enabled

    def set_system_prompt(self, prompt: str) -> None:
        """Set a custom system prompt.

        :param prompt: The new system prompt.
        """
        self._conversation.set_system_prompt(prompt)

    def set_temperature(self, temperature: float) -> None:
        """Set the sampling temperature.

        :param temperature: The new temperature.
        """
        self._temperature = temperature

    def set_max_tokens(self, max_tokens: int) -> None:
        """Set the maximum response tokens.

        :param max_tokens: The new token cap.
        """
        self._max_tokens = max_tokens

    def set_model(self, model: str) -> None:
        """Set the model used for subsequent messages.

        :param model: The model id.
        """
        self._model = model

    def current_settings(self) -> dict[str, str]:
        """Return the current settings as display-ready label/value pairs.

        :returns: An ordered mapping of setting name to its current value.
        """
        return {
            "Model": self._model,
            "Temperature": "default" if self._temperature is None else str(self._temperature),
            "Max tokens": "default" if self._max_tokens is None else str(self._max_tokens),
            "History": "on" if self._history_enabled else "off",
            "Exchanges stored": str(self._conversation.exchange_count),
            "System prompt": self._conversation.system_prompt,
        }
