"""SQL Assistant service: business logic for SQL-related capabilities.

Like ExplainService, a chosen capability selects the system prompt; the user's
SQL is the input. The Capability enum reuses the shared LabeledEnum base, so it
carries no duplicated labels()/from_choice() code. No I/O, no printing.
"""

import logging

from enums import LabeledEnum
from llm import LLMClient, Message
from prompts.sql import (
    explain_prompt,
    indexes_prompt,
    optimize_prompt,
    orm_prompt,
    performance_prompt,
    query_plan_prompt,
)

logger = logging.getLogger("m2_prompt_studio")


class Capability(LabeledEnum):
    """What the assistant can do with a SQL query. Definition order = menu order."""

    EXPLAIN = "Explain SQL"
    OPTIMIZE = "Optimize SQL"
    INDEXES = "Suggest Indexes"
    ORM = "Convert SQL <-> Django ORM"
    QUERY_PLAN = "Explain Query Plan"
    PERFORMANCE = "Performance Tips"


# Which system prompt builder to use for each capability.
_PROMPT_BUILDERS = {
    Capability.EXPLAIN: explain_prompt,
    Capability.OPTIMIZE: optimize_prompt,
    Capability.INDEXES: indexes_prompt,
    Capability.ORM: orm_prompt,
    Capability.QUERY_PLAN: query_plan_prompt,
    Capability.PERFORMANCE: performance_prompt,
}


class SQLAssistantService:
    """Applies a chosen capability's system prompt to a user-supplied SQL query."""

    def __init__(self, llm: LLMClient) -> None:
        """Initialize the service with an LLM client.

        :param llm: The client used to send messages to the model.
        """
        self._llm = llm

    def run(self, sql: str, capability: Capability) -> str | None:
        """Apply ``capability`` to ``sql`` and return the model's reply.

        :param sql: The SQL query (or Django ORM code) supplied by the user.
        :param capability: The capability to apply.
        :returns: The assistant's reply text, or ``None`` if the request failed.
        """
        messages = self._build_messages(sql, capability)
        logger.info("SQL request (capability=%s, sql_len=%d)", capability.name, len(sql))
        return self._llm.get_reply(messages)

    def _build_messages(self, sql: str, capability: Capability) -> list[Message]:
        """Assemble the capability (system) + SQL (user) messages.

        :param sql: The SQL query supplied by the user.
        :param capability: The capability whose system prompt should be used.
        :returns: Chat messages ready for the LLM client.
        """
        return [
            {"role": "system", "content": _PROMPT_BUILDERS[capability]()},
            {"role": "user", "content": sql},
        ]
