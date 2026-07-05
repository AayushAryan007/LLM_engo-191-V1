import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

SYSTEM_PROMPT = (
    "You are a helpful, concise assistant chatting with a user in a terminal."
)


def setup_logging() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("m1_cli_chat")


def require_api_key(logger: logging.Logger) -> str:
    if not GROQ_API_KEY:
        logger.error("API_KEY is missing. Set it in your .env file.")
        sys.exit(1)
    return GROQ_API_KEY
