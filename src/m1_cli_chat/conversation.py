from config import SYSTEM_PROMPT


class Conversation:
    def __init__(self, system_prompt: str = SYSTEM_PROMPT):
        self.history: list[dict] = [{"role": "system", "content": system_prompt}]

    def add_user_message(self, content: str) -> None:
        self.history.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        self.history.append({"role": "assistant", "content": content})

    def get_messages(self) -> list[dict]:
        return self.history
