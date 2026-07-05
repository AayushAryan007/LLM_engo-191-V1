"""Groq API client wrapper.

This is the only module that knows Groq (via the OpenAI-compatible SDK)
exists. It knows nothing about menus, prompts, or business logic: it takes
chat messages and returns the assistant's text.
"""

import logging

from openai import APIConnectionError, APIError, OpenAI, RateLimitError

from config import Settings

logger = logging.getLogger("m2_prompt_studio")

Message = dict[str, str]


class LLMClient:
    """Thin wrapper around the OpenAI-compatible Groq chat completions API."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the client from application settings.

        :param settings: Configuration providing the API key, base URL, and model.
        """
        self._client = OpenAI(api_key=settings.api_key, base_url=settings.base_url)
        self._model = settings.model

    def get_reply(self, messages: list[Message]) -> str | None:
        """Send a conversation to the model and return its reply.

        :param messages: Chat messages in OpenAI format, each a dict with
            ``role`` and ``content`` keys.
        :returns: The assistant's reply text, or ``None`` if the request failed.
        """
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
            )
            return response.choices[0].message.content
        except RateLimitError:
            logger.error("Rate limit hit. Try again shortly.")
        except APIConnectionError:
            logger.error("Could not reach Groq. Check your internet connection.")
        except APIError as e:
            logger.error("Groq API error: %s", e)
        return None
