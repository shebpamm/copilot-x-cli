"""Get bearer token"""
import requests


def get_bearer():
    headers = {
        "authorization": "token _REMOVED",
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
