# Work-in-progress CLI for Copilot X Chat

This is an unofficial CLI for using Copilot X Chat through the CLI, as I don't use VSCode.

Install it using `poetry install` or use the nix flake provided with `poetry2nix`.
You need to be in the Copilot X Chat Preview program for this to work.

```shell
Usage: x-cli [OPTIONS] COMMAND [ARGS]...

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                                            │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.                     │
│ --help                        Show this message and exit.                                                                          │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ chat                    Open an interactive chat session.                                                                          │
│ prompt                  Entrypoint.                                                                                                │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
