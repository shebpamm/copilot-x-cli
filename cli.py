"""CLI interface for using copilot-x chat."""
import typer

import api


def main(
    prompt: str = typer.Option(..., prompt=True),
    shell: bool = False,
    chat: bool = False,
    explain: bool = False,
):
    """
    Entrypoint.

    Args:
        prompt (str): Prompt to send to copilot
    """

    query = api.ChatQuery(prompt, shell=shell, chat=chat, explain=explain)

    print(query.get_answer_blocking())


if __name__ == "__main__":
    typer.run(main)
