"""Backend Mentor service: business logic for topic-based mentorship.

Pairs the fixed mentor persona with a chosen topic and calls the LLM. Unlike
ExplainService, there is no enum: every topic uses the same system prompt, so
the topics are plain data (a list of labels), not a type that drives behavior.
No I/O, no printing — a topic goes in, a reply comes out.
"""

import logging

from llm import LLMClient, Message
from prompts.backend import mentor_prompt

logger = logging.getLogger("m2_prompt_studio")

# Mentorable topics, in menu order. The chosen label is passed to the model
# verbatim as the subject to mentor on.
TOPICS: list[str] = [
    "Python",
    "Django",
    "Redis",
    "Celery",
    "Docker",
    "SQL",
    "PostgreSQL",
    "Nginx",
    "Git",
    "REST APIs",
    "Authentication",
    "Caching",
    "Logging",
    "System Design",
    "Performance",
]


class BackendMentorService:
    """Mentors on a chosen backend topic using a fixed Senior Mentor persona."""

    def __init__(self, llm: LLMClient) -> None:
        """Initialize the service with an LLM client.

        :param llm: The client used to send messages to the model.
        """
        self._llm = llm

    def run(self, topic: str) -> str | None:
        """Mentor on ``topic`` and return the model's reply.

        :param topic: The backend topic to mentor on (e.g. ``"Redis"``).
        :returns: The assistant's reply text, or ``None`` if the request failed.
        """
        messages = self._build_messages(topic)
        logger.info("Backend Mentor request (topic=%s)", topic)
        return self._llm.get_reply(messages)

    def _build_messages(self, topic: str) -> list[Message]:
        """Assemble the persona (system) + topic (user) messages.

        :param topic: The topic to mentor on.
        :returns: Chat messages ready for the LLM client.
        """
        return [
            {"role": "system", "content": mentor_prompt()},
            {"role": "user", "content": f"Mentor me on {topic}."},
        ]
