"""CLI interface for using copilot-x chat."""
import typer

from . import api
from .chat import ChatWindow

app = typer.Typer()


@app.command()
def main(
    prompt: str = typer.Option(..., prompt=True),
    shell: bool = False,
    chat: bool = False,
):
    """
    Entrypoint.

    Args:
        prompt (str): Prompt to send to copilot
    """
    chatSession = api.ChatSession(shell=shell, chat=chat)
    response = chatSession.send_chat_blocking(prompt)
    if chat:
        window = ChatWindow()
        with window.live:
            window.add_message(api.MessageRole.USER, prompt)
            window.add_message(api.MessageRole.ASSISTANT, response)

            while True:
                prompt = window.stream_prompt()
                window.add_message(api.MessageRole.USER, prompt)
                response = chatSession.send_chat_blocking(prompt)
                window.add_message(api.MessageRole.ASSISTANT, response)
    else:
        print(response)
