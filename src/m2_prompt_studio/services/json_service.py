"""JSON Generator service: generate and validate structured JSON output.

New element vs. other services: after the LLM replies, this service validates
the output with json.loads() and pretty-prints it, or reports why it was
invalid. Validation is business logic and lives here; display stays in
main/printer. No I/O, no printing.
"""

import json
import logging
from dataclasses import dataclass

from llm import LLMClient, Message
from prompts.json_mode import json_prompt

logger = logging.getLogger("m2_prompt_studio")


@dataclass(frozen=True)
class JSONResult:
    """Outcome of a JSON generation request.

    :param ok: True if the model returned valid, parseable JSON.
    :param content: Pretty-printed JSON when ``ok``, otherwise an error message.
    """

    ok: bool
    content: str


class JSONService:
    """Generates JSON from a natural-language request and validates it."""

    def __init__(self, llm: LLMClient) -> None:
        """Initialize the service with an LLM client.

        :param llm: The client used to send messages to the model.
        """
        self._llm = llm

    def run(self, request: str) -> JSONResult:
        """Generate JSON for ``request``, validate it, and return the outcome.

        :param request: A natural-language description of the desired JSON.
        :returns: A :class:`JSONResult` — valid pretty-printed JSON, or an error.
        """
        logger.info("JSON request (len=%d)", len(request))
        reply = self._llm.get_reply(self._build_messages(request))
        if reply is None:
            return JSONResult(False, "No reply from the model.")
        return self._validate(reply)

    def _build_messages(self, request: str) -> list[Message]:
        """Assemble the JSON (system) + request (user) messages.

        :param request: The user's natural-language request.
        :returns: Chat messages ready for the LLM client.
        """
        return [
            {"role": "system", "content": json_prompt()},
            {"role": "user", "content": request},
        ]

    def _validate(self, reply: str) -> JSONResult:
        """Parse ``reply`` as JSON and pretty-print it, or describe the error.

        :param reply: The raw text returned by the model.
        :returns: A valid :class:`JSONResult` on success, else an error result.
        """
        try:
            parsed = json.loads(reply)
        except json.JSONDecodeError as e:
            logger.warning("Model returned invalid JSON: %s", e)
            return JSONResult(False, f"Model did not return valid JSON: {e}")
        return JSONResult(True, json.dumps(parsed, indent=2))
