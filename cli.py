"""CLI interface for using copilot-x chat."""
import typer
import api


def main(prompt: str = typer.Option(..., prompt=True), shell: bool = False, chat: bool = False):
    """
    Entrypoint.

    Args:
        prompt (str): Prompt to send to copilot
    """

    print(api.get_answer_blocking(prompt))


if __name__ == "__main__":
    typer.run(main)
