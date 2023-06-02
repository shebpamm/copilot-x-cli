"""CLI interface for using copilot-x chat."""
from base64 import b64decode
from pathlib import Path

import typer

from . import actions, api
from .chat import ChatWindow

app = typer.Typer()


@app.command()
def chat():
    """Open an interactive chat session."""
    chatSession = api.ChatSession(chat=True)
    window = ChatWindow()
    with window.live:
        while True:
            prompt = window.stream_prompt()
            window.add_message(api.MessageRole.USER, prompt)
            response = chatSession.send_chat_blocking(prompt)
            window.add_message(api.MessageRole.ASSISTANT, response)


@app.command()
def prompt(
    question: str = typer.Option(..., prompt=True),
    base64: bool = False,
    shell: bool = False,
    chat: bool = False,
    code: bool = False,
):
    """
    Entrypoint.

    Args:
        prompt (str): Prompt to send to copilot
        shell (bool): Whether to add special shell instructions
        chat (bool): Whether to add chat instructions
        code (bool): Whether to add code instructions
    """

    if base64:
        question = b64decode(question).decode("utf-8")

    chatSession = api.ChatSession(shell=shell, chat=chat, code=code)
    response = chatSession.send_chat_blocking(question)
    print(response)


@app.command()
def action(
    selection: str,
    prompt: str = typer.Option(..., prompt=True),
    base64: bool = False,
    json: bool = False,
):
    """
    Prompt for an action, classify it and run related prompt with code context.

    The arguments are a bit confusing, as the base64 is used for providing input in an encoded format but the json flag is used to output a json object.
    """
    if base64:
        prompt = b64decode(prompt).decode("utf-8")

    sel = actions.parse_selection(selection)

    action = actions.PromptAction(prompt, sel)

    response = action.perform()

    if json:
        print(response.json())
    else:
        print(response.answer)
