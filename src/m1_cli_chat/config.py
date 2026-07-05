import logging
import os

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

SYSTEM_PROMPT: str = (
    "You are a helpful, concise assistant chatting with a user in a terminal."
)


class ConfigError(Exception):
    """Raised when required configuration (e.g. an API key) is missing or invalid."""


def setup_logging() -> logging.Logger:
    """Configure root logging and return the application logger.

    :returns: The ``m1_cli_chat`` logger, ready for use by callers.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("m1_cli_chat")


def require_api_key() -> str:
    """Return the configured Groq API key.

    :returns: The API key loaded from the ``GROQ_API_KEY`` environment variable.
    :raises ConfigError: If ``GROQ_API_KEY`` is not set.
    """
    if not GROQ_API_KEY:
        raise ConfigError("GROQ_API_KEY is missing. Set it in your .env file.")
    return GROQ_API_KEY
