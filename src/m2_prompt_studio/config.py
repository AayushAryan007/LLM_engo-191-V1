"""Application configuration: environment loading, settings, and logging.

This is the single source of truth for runtime configuration. Every other
module reads settings from here rather than touching ``os.environ`` directly.
"""

import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

_DEFAULT_MODEL = "llama-3.1-8b-instant"
_DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"

# Groq models selectable in the Playground. Edit to match your Groq access.
AVAILABLE_MODELS: list[str] = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "gemma2-9b-it",
]


class ConfigError(Exception):
    """Raised when required configuration (e.g. the API key) is missing."""


@dataclass(frozen=True)
class Settings:
    """Immutable snapshot of the configuration the app needs to run.

    :param api_key: Groq API key used to authenticate requests.
    :param model: Chat completion model identifier.
    :param base_url: OpenAI-compatible base URL for the Groq API.
    """

    api_key: str
    model: str
    base_url: str


def get_settings() -> Settings:
    """Read and validate configuration from the environment.

    :returns: A populated :class:`Settings` instance.
    :raises ConfigError: If ``GROQ_API_KEY`` is not set.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ConfigError("GROQ_API_KEY is missing. Set it in your .env file.")

    return Settings(
        api_key=api_key,
        model=os.getenv("GROQ_MODEL", _DEFAULT_MODEL),
        base_url=os.getenv("GROQ_BASE_URL", _DEFAULT_BASE_URL),
    )


def setup_logging() -> logging.Logger:
    """Configure application-wide logging and return the app logger.

    :returns: The ``m2_prompt_studio`` logger, ready for use by callers.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("m2_prompt_studio")
