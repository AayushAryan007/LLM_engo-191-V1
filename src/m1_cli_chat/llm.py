import logging

from openai import APIError, APIConnectionError, OpenAI, RateLimitError

from config import GROQ_BASE_URL, GROQ_MODEL

logger = logging.getLogger("m1_cli_chat")


class LLMClient:
    """Thin wrapper around the OpenAI-compatible Groq chat completions API."""

    def __init__(self, api_key: str) -> None:
        """Initialize the client.

        :param api_key: Groq API key used to authenticate requests.
        """
        self.client: OpenAI = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
        self.model: str = GROQ_MODEL

    def get_reply(self, messages: list[dict[str, str]]) -> str | None:
        """Send a conversation to the model and return its reply.

        :param messages: Chat messages in OpenAI format, each a dict with
            ``role`` and ``content`` keys.
        :returns: The assistant's reply text, or ``None`` if the request failed
            (rate limit, connection error, or other API error).
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
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
