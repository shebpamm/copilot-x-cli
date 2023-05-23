import json
from auth import get_bearer
from constants import BASE_INSTRUCTION, SHELL_INSTRUCTION
from errors import TokenExpirationError

import requests

headers = {
    "x-request-id": "9d4f79c9-7104-4e24-a3ac-73349f95af63",
    "openai-organization": "github-copilot",
    "vscode-sessionid": "9188b680-9c71-402e-9e9d-f6d3a99f71f91684844091941",
    "vscode-machineid": "859856161997d243b5f349338d1bd485b6d2664faa24bed9c1f09bdff6dddb08",
    "editor-version": "vscode/1.79.0-insider",
    "editor-plugin-version": "copilot/0.1.2023052205",
    "openai-intent": "conversation-panel",
    "content-type": "application/json",
    "user-agent": "GithubCopilot/0.1.2023052205",
    "accept": "*/*",
}

json_data = {
    "intent": True,
    "messages": [
        {
            "content": BASE_INSTRUCTION,
            "role": "system",
        },
        {
            "content": SHELL_INSTRUCTION,
            "role": "system",
        },
    ],
    "model": "copilot-chat",
    "n": 1,
    "stream": True,
    "temperature": 0.1,
    "top_p": 1,
}


def get_answer_stream(prompt, state=json_data):
    bearer_token = get_bearer()
    headers["authorization"] = f"Bearer {bearer_token}"

    state["messages"].append({"content": prompt, "role": "user"})

    s = requests.Session()

    return s.post(
        "https://copilot-proxy.githubusercontent.com/v1/chat/completions",
        headers=headers,
        json=json_data,
        stream=True,
    )


def get_answer_blocking(prompt):
    answer = ""
    with get_answer_stream(prompt) as resp:
        for line in resp.iter_lines():
            if line == b"token expired":
                raise TokenExpirationError
            if line == b"data: [DONE]":
                break

            if line.startswith(b"data:"):
                chunk = json.loads(line.split(b"data:")[1])
                delta = chunk["choices"][0]["delta"]
                if "content" in delta:
                    answer += delta["content"]

    return answer