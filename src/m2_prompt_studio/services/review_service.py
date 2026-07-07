"""Code Reviewer service: business logic for persona-based code review.

Like SQLAssistantService, a chosen review mode selects the system prompt; the
user's code is the input. ReviewMode reuses the shared LabeledEnum base, so it
carries no duplicated labels()/from_choice() code. No I/O, no printing.
"""

import logging

from enums import LabeledEnum
from llm import LLMClient, Message
from prompts.review import (
    clean_code_prompt,
    faang_prompt,
    performance_prompt,
    pythonic_prompt,
    security_prompt,
    senior_backend_prompt,
    startup_prompt,
)

logger = logging.getLogger("m2_prompt_studio")


class ReviewMode(LabeledEnum):
    """Reviewer personas. Definition order = menu order."""

    STARTUP = "Startup"
    SENIOR_BACKEND = "Senior Backend Engineer"
    FAANG = "FAANG Reviewer"
    PERFORMANCE = "Performance Engineer"
    SECURITY = "Security Engineer"
    CLEAN_CODE = "Clean Code Reviewer"
    PYTHONIC = "Pythonic Style Reviewer"


# Which system prompt builder to use for each review mode.
_PROMPT_BUILDERS = {
    ReviewMode.STARTUP: startup_prompt,
    ReviewMode.SENIOR_BACKEND: senior_backend_prompt,
    ReviewMode.FAANG: faang_prompt,
    ReviewMode.PERFORMANCE: performance_prompt,
    ReviewMode.SECURITY: security_prompt,
    ReviewMode.CLEAN_CODE: clean_code_prompt,
    ReviewMode.PYTHONIC: pythonic_prompt,
}


class ReviewService:
    """Reviews user-supplied code using a chosen reviewer persona."""

    def __init__(self, llm: LLMClient) -> None:
        """Initialize the service with an LLM client.

        :param llm: The client used to send messages to the model.
        """
        self._llm = llm

    def run(self, code: str, mode: ReviewMode) -> str | None:
        """Review ``code`` in the given ``mode`` and return the model's reply.

        :param code: The code snippet supplied by the user.
        :param mode: The reviewer persona to apply.
        :returns: The assistant's reply text, or ``None`` if the request failed.
        """
        messages = self._build_messages(code, mode)
        logger.info("Code review request (mode=%s, code_len=%d)", mode.name, len(code))
        return self._llm.get_reply(messages)

    def _build_messages(self, code: str, mode: ReviewMode) -> list[Message]:
        """Assemble the reviewer (system) + code (user) messages.

        :param code: The code snippet supplied by the user.
        :param mode: The reviewer persona whose system prompt should be used.
        :returns: Chat messages ready for the LLM client.
        """
        return [
            {"role": "system", "content": _PROMPT_BUILDERS[mode]()},
            {"role": "user", "content": code},
        ]
