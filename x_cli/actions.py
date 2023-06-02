import random
import re
import string
import json
from enum import Enum
from pathlib import Path

from pygments.lexers import get_lexer_for_filename
from pygments.token import Comment

from .api import ChatSession, MessageRole
from .constants import ACTION_INSTRUCTION, CLASSIFY_INSTRUCTION

EXTENSTIONS_FILE = Path(__file__).parent / "extensions.json"


class PromptType(Enum):
    # 1) "code" if the coworker should add new code to an already existing code base
    # 2) "documentation" if the coworker should add documentation to already existing code
    # 3) "edit" if the coworker should replace existing code
    # 4) "test" if the coworker should create a new test case for already existing code
    # 5) "explain" if the coworker should explain existing code
    # 6) "fix" if the coworker should correct a problem in existing code
    # 7) "unknown" for everything else
    CODE = "code"
    DOCUMENTATION = "documentation"
    EDIT = "edit"
    TEST = "test"
    EXPLAIN = "explain"
    FIX = "fix"
    UNKNOWN = "unknown"


class ActionResponse:
    def __init__(self, answer: str, prompt_type: PromptType):
        self.answer = answer
        self.type = prompt_type

    def json(self):
        return json.dumps({
            "answer": self.answer,
            "type": self.type.value,
        })


class CursorPosition:
    """Represents a single cursors position in a specific file."""

    def __init__(self, line: int):
        self.line = line - 1


class FileSelection:
    """
    Represents a selection of a file.

    The selection is defined by a start and end cursor position.
    Currently the whole lines are selected.
    Provides helper functions to get content from the file.
    """

    def __init__(self, file: str, start: CursorPosition, end: CursorPosition):
        self.file = Path(file)
        self.start = start
        self.end = end
        self.content = self.read_content()

    def read_content(self):
        with open(self.file, "r") as f:
            return f.readlines()

    def is_above(self):
        return self.start.line == 0

    def is_below(self):
        return self.end.line == len(self.content) - 1

    def get_above(self):
        return self._format(self.content[: self.start.line])

    def get_below(self):
        return self._format(self.content[self.end.line :])

    def get_selection(self):
        return self._format(self.content[self.start.line : self.end.line])

    def _format(self, lines):
        return "".join(lines)

    def __str__(self):
        return f"{self.file}:{self.start.line}-{self.end.line}"


class PromptAction:
    def __init__(self, prompt: str, selection: FileSelection):
        self.prompt = prompt
        self.selection = selection
        self.session = ChatSession(base=False)

    def perform(self) -> ActionResponse:
        self._void_session()
        self._classify()
        self._detect_language()

        match self.type:  # noqa: E999
            case PromptType.CODE:
                return self._code()
            case PromptType.DOCUMENTATION:
                return self._documentation()
            case PromptType.EDIT:
                return self._edit()
            case PromptType.TEST:
                return self._test()
            case PromptType.EXPLAIN:
                return self._explain()
            case PromptType.FIX:
                return self._fix()
            case PromptType.UNKNOWN:
                return self._unknown()

    def _classify(self):
        """Classify a prompt as one of the PromptTypes."""
        self.session.add_message(CLASSIFY_INSTRUCTION, MessageRole.SYSTEM)
        answer = self.session.send_chat_blocking(f"<<< {self.prompt} >>>")
        match answer:  # noqa: E999
            case "code":
                self.type = PromptType.CODE
            case "documentation":
                self.type = PromptType.DOCUMENTATION
            case "edit":
                self.type = PromptType.EDIT
            case "test":
                self.type = PromptType.TEST
            case "explain":
                self.type = PromptType.EXPLAIN
            case "fix":
                self.type = PromptType.FIX
            case _:
                self.type = PromptType.UNKNOWN

    def _ask(self, extract_code=False):
        anchor = self._generate_anchor()
        begin_anchor = f"{self.comment_character} BEGIN: {anchor}"
        end_anchor = f"{self.comment_character} END: {anchor}"
        """Replace existing code."""
        self._void_session()
        self.session.add_message(ACTION_INSTRUCTION, MessageRole.SYSTEM)
        if self.selection.is_above():
            self.session.add_message(
                f"""
                     I have the following code above the selection:
                     ```{self.language}
                     {self.comment_character} FILEPATH: {self.selection.file}
                     {self.selection.get_above()}
                     ```
                     """,
                MessageRole.USER,
            )

        self.session.add_message(
            f"""
                 I have the following code in the selection:
                 ```{self.language}
                 {self.comment_character} FILEPATH: {self.selection.file}
                 {begin_anchor}
                 {self.selection.get_selection()}
                 {end_anchor}
                 ```
                 """,
            MessageRole.USER,
        )
        if self.selection.is_below():
            self.session.add_message(
                f"""
                     I have the following code below the selection:
                     ```{self.language}
                     {self.comment_character} FILEPATH: {self.selection.file}
                     {self.selection.get_selection()}
                     ```
                     """,
                MessageRole.USER,
            )
        response = self.session.send_chat_blocking(self.prompt)
        if extract_code:
            return self._extract_anchors(response, anchor)
        else:
            return response.replace(begin_anchor, "").replace(end_anchor, "")

    def _detect_language(self):
        """Detect the language based on the file extension."""
        self.lexer = get_lexer_for_filename(self.selection.file)
        if len(self.lexer.aliases):  # type: ignore
            self.language = self.lexer.aliases[0]  # type: ignore
        else:
            self.language = self.lexer.name  # type: ignore

        self.comment_regex = ""

        for _, category in self.lexer.tokens.items():  # type: ignore
            for token in category:
                if isinstance(token, tuple):
                    if token[1] == Comment.Single:
                        self.comment_regex = token[0]

        # Remove non-capturing groups
        comment_character = self.comment_regex.replace("(?:", "")

        # Remove all '.+*?^$()[]{}' characters from the regex
        self.comment_character = comment_character.translate(
            str.maketrans("", "", ".+*?^$()[]{}")
        )

    def _void_session(self):
        """Rewrite the message history of the session"""
        self.session.state["messages"] = []

    def _generate_anchor(self):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def _extract_anchors(self, data: str, anchor: str) -> str:
        """Get content between anchors in file."""
        begin_anchor = f"{self.comment_character} BEGIN: {anchor}"
        end_anchor = f"{self.comment_character} END: {anchor}"
        res = re.search(f"{begin_anchor}(.*){end_anchor}", data, re.DOTALL)
        if res:
            return res.group(1).strip("\n")
        else:
            raise ValueError(
                f"Could not find anchors {begin_anchor} and {end_anchor} in {data}"
            )

    def _code(self):
        """Add new code to an already existing code base."""
        answer = self._ask(extract_code=True)
        return ActionResponse(answer, PromptType.CODE)

    def _documentation(self):
        """Add documentation to already existing code."""
        answer = self._ask(extract_code=True)
        return ActionResponse(answer, PromptType.DOCUMENTATION)

    def _edit(self):
        """Edit existing code."""
        answer = self._ask(extract_code=True)
        return ActionResponse(answer, PromptType.EDIT)

    def _test(self):
        """Create a new test case for already existing code."""
        answer = self._ask(extract_code=True)
        return ActionResponse(answer, PromptType.TEST)

    def _explain(self):
        """Explain existing code."""
        answer = self._ask()
        return ActionResponse(answer, PromptType.EXPLAIN)

    def _fix(self):
        """Correct a problem in existing code."""
        answer = self._ask(extract_code=True)
        return ActionResponse(answer, PromptType.FIX)

    def _unknown(self):
        """Unknown prompt type."""
        answer = self._ask()
        return ActionResponse(answer, PromptType.UNKNOWN)


def parse_selection(raw_selection: str) -> FileSelection:
    """
    Create a FileSelection object.
    """

    file, lines = raw_selection.split(":")

    start, end = lines.split("-")
    try:
        return FileSelection(file, CursorPosition(int(start)), CursorPosition(int(end)))
    except ValueError:
        raise ValueError("Invalid selection format. Expected <line>:<column>")
