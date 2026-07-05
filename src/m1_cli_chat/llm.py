import logging

from openai import APIError, APIConnectionError, OpenAI, RateLimitError

from config import GROQ_BASE_URL, GROQ_MODEL

logger = logging.getLogger("m1_cli_chat")


class LLMClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
        self.model = GROQ_MODEL

    def get_reply(self, messages: list[dict]) -> str | None:
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
