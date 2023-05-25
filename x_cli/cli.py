"""CLI interface for using copilot-x chat."""
import typer

from . import api
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
    chatSession = api.ChatSession(shell=shell, chat=chat, code=code)
    response = chatSession.send_chat_blocking(question)
    print(response)
