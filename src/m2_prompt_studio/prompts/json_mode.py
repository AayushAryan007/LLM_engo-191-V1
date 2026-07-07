"""System prompt for the JSON Generator module.

Instructs the model to return only valid JSON. Pure function: text out only —
no API calls, no input(), no printing.
"""


def json_prompt() -> str:
    """System prompt forcing JSON-only output."""
    return (
        "You are a JSON generation engine. Given the user's request, respond "
        "with a single valid JSON value that satisfies it. Output only the "
        "JSON: no explanations, no comments, and no Markdown code fences. The "
        "JSON must be syntactically valid and directly parseable."
    )
