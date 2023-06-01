import math
import shutil

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown

from .api import MessageRole


def getch():
    import sys
    import termios

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = [
        old[0],
        old[1],
        old[2],
        2608,
        15,
        15,
        [
            b"\x03",
            b"\x1c",
            b"\x7f",
            b"\x15",
            b"\x04",
            0,
            1,
            b"\x00",
            b"\x11",
            b"\x13",
            b"\x1a",
            b"\x00",
            b"\x12",
            b"\x0f",
            b"\x17",
            b"\x16",
            b"\x00",
            b"\x00",
            b"\x00",
            b"\x00",
            b"\x00",
            b"\x00",
            b"\x00",
            b"\x00",
            b"\x00",
            b"\x00",
            b"\x00",
            b"\x00",
            b"\x00",
            b"\x00",
            b"\x00",
            b"\x00",
        ],
    ]
    try:
        termios.tcsetattr(fd, termios.TCSADRAIN, new)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


row_styles = {
    MessageRole.ASSISTANT: "white on black",
    MessageRole.USER: "white on default",
    MessageRole.SYSTEM: "white on red",
}


class ChatWindow:
    def __init__(self):
        self.console = Console()
        self.table = self._make_table()
        self.input = self._make_input()
        self.layout = self._make_layout()
        self.live = Live(self.layout, refresh_per_second=30, screen=True)

    def _make_table(self):
        terminal_width = shutil.get_terminal_size().columns
        table_width = math.floor(terminal_width * 0.8)

        table = Table(title="Chat", show_header=False)

        table.add_column("Role", no_wrap=True, width=3)
        table.add_column("Message", width=table_width)

        return table

    def _make_layout(self):
        layout = Layout()
        layout.split_column(
            Layout(name="history", ratio=1),
            Layout(name="input", size=3),
        )
        layout["history"].update(self.table)
        layout["input"].update(self.input)

        return layout

    def _make_input(self):
        self.text = Text("")
        panel = Panel(self.text, title_align="left", title="> ")

        return panel

    def render(self):
        self.live.update(self.layout)

    def stream_prompt(self) -> str:
        while True:
            ch = getch()
            if ch.isprintable():
                self.text.append(ch)
                self.render()
            elif ch == "\x7f":
                # If backspace, crop last ch
                self.text.right_crop()
                self.render()
            elif ch == "\n":
                text = self.text.plain
                self.text.truncate(0)
                self.render()
                return text
            elif ch == "\x03" or ch == "\x04":
                # If ctrl-c or ctrl-d, exit
                raise KeyboardInterrupt

    def add_message(self, role: MessageRole, message: str):
        match role: # noqa: E999
            case MessageRole.ASSISTANT:
                role_name = "[bold]AI[not bold]"
            case MessageRole.USER:
                role_name = "[bold]You[not bold]"
            case MessageRole.SYSTEM:
                role_name = "[bold]SYS[not bold]"

        content = Markdown(message)
        self.table.add_row(role_name, content, style=row_styles[role])

        return self
