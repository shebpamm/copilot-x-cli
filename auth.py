"""Get bearer token"""
import requests
import os


def get_copilot_token():
    """Get copilot token from environment variable."""
    return os.environ.get("COPILOT_TOKEN")


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
