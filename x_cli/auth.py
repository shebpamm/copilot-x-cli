"""Get bearer token"""
import json
import os

import requests


def get_copilot_token():
    """
    Get copilot token.

    Firstly try getting it from COPILOT_TOKEN.
    If this fails, try getting it from ~/.config/github-copilot/hosts.json
    """
    if "COPILOT_TOKEN" in os.environ:
        return os.environ["COPILOT_TOKEN"]
    else:
        try:
            with open(os.path.expanduser("~/.config/github-copilot/hosts.json")) as f:
                data = json.load(f)
                return data["github.com"]["oauth_token"]
        except FileNotFoundError:
            raise Exception(
                "Please set COPILOT_TOKEN environment variable or install Github Copilot extension"
            )


def get_bearer():
    copilot_token = get_copilot_token()
    headers = {
        "authorization": f"token {copilot_token}",
        "editor-version": "vscode/1.79.0-insider",
        "editor-plugin-version": "copilot/1.86.112",
        "user-agent": "GithubCopilot/1.86.112",
        "accept": "*/*",
    }

    response = requests.get(
        "https://api.github.com/copilot_internal/v2/token", headers=headers
    )
    data = response.json()

    return data["token"]
