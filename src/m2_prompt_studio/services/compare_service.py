"""Prompt Comparison service: run one question through several prompt strategies.

New element: this service makes multiple LLM calls in a single action and
reuses existing prompt functions (from explain.py and backend.py) rather than
defining new ones. It aggregates labeled answers; main displays them. No I/O,
no printing.
"""

import logging
from collections.abc import Callable

from llm import LLMClient, Message
from prompts.backend import mentor_prompt
from prompts.compare import default_prompt
from prompts.explain import (
    interview_prompt,
    non_technical_prompt,
    senior_prompt,
    student_prompt,
)

logger = logging.getLogger("m2_prompt_studio")

# A labeled answer; the answer is None if that strategy's call failed.
Comparison = tuple[str, str | None]

# Ordered comparison strategies: (label, system prompt builder). Every prompt
# except "Normal" is reused from an existing module.
_STRATEGIES: list[tuple[str, Callable[[], str]]] = [
    ("Normal", default_prompt),
    ("Student", student_prompt),
    ("Backend Mentor", mentor_prompt),
    ("Interview", interview_prompt),
    ("Senior Engineer", senior_prompt),
    ("Non-Technical", non_technical_prompt),
]


class CompareService:
    """Runs one question through several prompt strategies and collects answers."""

    def __init__(self, llm: LLMClient) -> None:
        """Initialize the service with an LLM client.

        :param llm: The client used to send messages to the model.
        """
        self._llm = llm

    def run(self, question: str) -> list[Comparison]:
        """Answer ``question`` under each strategy and return labeled results.

        :param question: The question to run through every strategy.
        :returns: One ``(label, answer)`` pair per strategy, in strategy order.
        """
        logger.info(
            "Prompt comparison (%d strategies, question_len=%d)",
            len(_STRATEGIES),
            len(question),
        )
        results: list[Comparison] = []
        for label, build_prompt in _STRATEGIES:
            reply = self._llm.get_reply(self._build_messages(build_prompt(), question))
            results.append((label, reply))
        return results

    def _build_messages(self, system_prompt: str, question: str) -> list[Message]:
        """Assemble the strategy (system) + question (user) messages.

        :param system_prompt: The system prompt for this strategy.
        :param question: The user's question.
        :returns: Chat messages ready for the LLM client.
        """
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ]
