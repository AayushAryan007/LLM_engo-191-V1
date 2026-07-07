"""Explain Concepts service: business logic for the audience-aware explainer.

Owns the mapping from audience to system prompt and the assembly of chat
messages. No I/O, no printing — a topic and an audience go in, a reply comes out.
"""

import logging

from enums import LabeledEnum
from llm import LLMClient, Message
from prompts.explain import (
    backend_prompt,
    interview_prompt,
    non_technical_prompt,
    senior_prompt,
    student_prompt,
)

logger = logging.getLogger("m2_prompt_studio")


class Audience(LabeledEnum):
    """Audiences an explanation can be tailored to. Definition order = menu order."""

    STUDENT = "Student"
    BACKEND = "Backend Developer"
    SENIOR = "Senior Engineer"
    INTERVIEW = "Interview Preparation"
    NON_TECHNICAL = "Non Technical Person"


# Which system prompt builder to use for each audience.
_PROMPT_BUILDERS = {
    Audience.STUDENT: student_prompt,
    Audience.BACKEND: backend_prompt,
    Audience.SENIOR: senior_prompt,
    Audience.INTERVIEW: interview_prompt,
    Audience.NON_TECHNICAL: non_technical_prompt,
}


class ExplainService:
    """Explains a topic, tailoring the system prompt to the chosen audience."""

    def __init__(self, llm: LLMClient) -> None:
        """Initialize the service with an LLM client.

        :param llm: The client used to send messages to the model.
        """
        self._llm = llm

    def run(self, topic: str, audience: Audience) -> str | None:
        """Explain ``topic`` for ``audience`` and return the model's reply.

        :param topic: The concept to explain (e.g. ``"Docker"``).
        :param audience: The audience the explanation is tailored to.
        :returns: The assistant's reply text, or ``None`` if the request failed.
        """
        messages = self._build_messages(topic, audience)
        logger.info("Explain request (audience=%s, topic=%s)", audience.name, topic)
        return self._llm.get_reply(messages)

    def _build_messages(self, topic: str, audience: Audience) -> list[Message]:
        """Assemble the system + user messages for the request.

        :param topic: The concept to explain.
        :param audience: The audience whose system prompt should be used.
        :returns: Chat messages ready for the LLM client.
        """
        system_prompt = _PROMPT_BUILDERS[audience]()
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Explain {topic}."},
        ]
