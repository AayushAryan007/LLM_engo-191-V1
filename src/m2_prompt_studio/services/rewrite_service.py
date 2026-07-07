"""Rewrite Assistant service: business logic for style-based text rewriting.

Like SQLAssistantService, a chosen style selects the system prompt; the user's
text is the input. RewriteStyle reuses the shared LabeledEnum base. No I/O,
no printing.
"""

import logging

from enums import LabeledEnum
from llm import LLMClient, Message
from prompts.rewrite import (
    ats_resume_prompt,
    documentation_prompt,
    email_prompt,
    executive_summary_prompt,
    linkedin_prompt,
    professional_prompt,
    simplified_prompt,
)

logger = logging.getLogger("m2_prompt_studio")


class RewriteStyle(LabeledEnum):
    """Rewrite styles. Definition order = menu order."""

    PROFESSIONAL = "Professional"
    DOCUMENTATION = "Documentation"
    ATS_RESUME = "ATS Resume"
    LINKEDIN = "LinkedIn"
    EMAIL = "Email"
    SIMPLIFIED = "Simplified English"
    EXECUTIVE_SUMMARY = "Executive Summary"


# Which system prompt builder to use for each style.
_PROMPT_BUILDERS = {
    RewriteStyle.PROFESSIONAL: professional_prompt,
    RewriteStyle.DOCUMENTATION: documentation_prompt,
    RewriteStyle.ATS_RESUME: ats_resume_prompt,
    RewriteStyle.LINKEDIN: linkedin_prompt,
    RewriteStyle.EMAIL: email_prompt,
    RewriteStyle.SIMPLIFIED: simplified_prompt,
    RewriteStyle.EXECUTIVE_SUMMARY: executive_summary_prompt,
}


class RewriteService:
    """Rewrites user-supplied text in a chosen style."""

    def __init__(self, llm: LLMClient) -> None:
        """Initialize the service with an LLM client.

        :param llm: The client used to send messages to the model.
        """
        self._llm = llm

    def run(self, text: str, style: RewriteStyle) -> str | None:
        """Rewrite ``text`` in the given ``style`` and return the model's reply.

        :param text: The text supplied by the user.
        :param style: The rewrite style to apply.
        :returns: The assistant's reply text, or ``None`` if the request failed.
        """
        messages = self._build_messages(text, style)
        logger.info("Rewrite request (style=%s, text_len=%d)", style.name, len(text))
        return self._llm.get_reply(messages)

    def _build_messages(self, text: str, style: RewriteStyle) -> list[Message]:
        """Assemble the style (system) + text (user) messages.

        :param text: The text supplied by the user.
        :param style: The style whose system prompt should be used.
        :returns: Chat messages ready for the LLM client.
        """
        return [
            {"role": "system", "content": _PROMPT_BUILDERS[style]()},
            {"role": "user", "content": text},
        ]
