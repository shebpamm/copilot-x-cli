import json
from enum import Enum

import requests

from .auth import get_bearer
from .constants import (BASE_INSTRUCTION, CHAT_INSTRUCTION, HEADERS,
                        SHELL_INSTRUCTION)
from .errors import TokenExpirationError


class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


json_data = {
    "intent": True,
    "messages": [],
    "model": "copilot-chat",
    "n": 1,
    "stream": True,
    "temperature": 0.1,
    "top_p": 1,
}


class ChatSession:
    def __init__(
        self,
        messages=[],
        shell: bool = False,
        chat: bool = False,
    ):
        self.shell = shell
        self.chat = chat

        self.bearer_token = get_bearer()
        self.state = self.init_state(messages)

    def init_state(self, messages=[]):
        state = json_data.copy()

        self.add_message(state, BASE_INSTRUCTION, MessageRole.SYSTEM)
        if self.shell:
            self.add_message(state, SHELL_INSTRUCTION, MessageRole.SYSTEM)
        if self.chat:
            self.add_message(state, CHAT_INSTRUCTION, MessageRole.SYSTEM)

        state["messages"] += messages

        return state

    def add_message(self, state, content: str, role: MessageRole):
        state["messages"].append({"content": content, "role": role.value})

    def get_answer_stream(self):
        HEADERS["authorization"] = f"Bearer {self.bearer_token}"

        s = requests.Session()

        return s.post(
            "https://copilot-proxy.githubusercontent.com/v1/chat/completions",
            headers=HEADERS,
            json=self.state,
            stream=True,
        )

    def send_chat_blocking(self, prompt):
        self.add_message(self.state, prompt, MessageRole.USER)

        # print(json.dumps(self.state, indent=4))
        answer = ""
        with self.get_answer_stream() as resp:
            for line in resp.iter_lines():
                if line == b"token expired":
                    raise TokenExpirationError
                if line == b"data: [DONE]":
                    break

                if line.startswith(b'{"error":{"code":"off_topic"'):
                    answer = "Answer was marked offtopic by API and not returned."
                    break

                if line.startswith(b"data:"):
                    chunk = json.loads(line.split(b"data:")[1])
                    delta = chunk["choices"][0]["delta"]
                    if "content" in delta:
                        answer += delta["content"]

        self.add_message(self.state, answer, MessageRole.ASSISTANT)

        return answer
