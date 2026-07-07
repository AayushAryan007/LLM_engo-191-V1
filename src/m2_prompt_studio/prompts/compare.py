"""Prompt(s) unique to the Prompt Comparison module.

The comparison reuses existing prompts (Student, Backend Mentor, Interview,
Senior, Non-Technical) from explain.py and backend.py. The only new prompt is
the plain "Normal" assistant baseline defined here. Pure function: text out
only — no API calls, no input(), no printing.
"""


def default_prompt() -> str:
    """System prompt: a plain, general-purpose assistant (the comparison baseline)."""
    return (
        "You are a helpful assistant. Answer the user's question clearly and "
        "concisely."
    )
