import datetime
import os
import subprocess
import sys
import tempfile
import textwrap
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

_COMMENT_STR_START = "<!--"
_COMMENT_STR_END = "-->"


def editor_input(
    data: str = "",
    comment: str = "",
    filename: str = "DEFAULT_FILENAME",
    editor: Sequence[str] | None = None,
) -> str:
    if not editor:
        editor_str = os.getenv("EDITOR") or os.getenv("VISUAL") or "vi"
        editor = [editor_str]
    comment = textwrap.dedent(comment)
    comment = "\n".join(
        textwrap.wrap(
            comment,
            width=79,
            replace_whitespace=False,
            break_long_words=False,
        )
    )
    comment = "\n".join(
        f"{_COMMENT_STR_START} {line} {_COMMENT_STR_END}"
        for line in comment.splitlines()
    )

    with tempfile.TemporaryDirectory() as tempdir_path:
        file_path = Path(tempdir_path) / filename

        file_path.write_text(f"{data}\n{comment}\n")

        subprocess.run([*editor, "--", str(file_path)])

        with file_path.open("r") as f:
            lines = f.readlines()
        res = "".join(line.partition(_COMMENT_STR_START)[0] for line in lines).strip()
        return res


def print_and_exit(*values: object, exit_code: int = 1) -> NoReturn:
    print(*values, file=sys.stderr)
    sys.exit(exit_code)


def write_post(argv: Sequence[str] | None = None) -> None:
    _ = argv
    graveyard = Path("./pages/index.html")
    if not graveyard.exists():
        print_and_exit("graveyard is missing; aborting")

    lines = graveyard.read_text().splitlines()
    post = editor_input(comment="write a post :)", filename="WRITE_A_POST.html")
    if not post:
        print_and_exit("empty post; aborting")

    i = -1
    for i, line in enumerate(lines):
        if '<div id="graveyard">' in line:
            break
    else:
        print_and_exit("no graveyard div; aborting")

    date_string = datetime.datetime.today().strftime("%Y-%m-%d")
    lines.insert(i + 1, f'  <div date="{date_string}">{post}</div>')

    graveyard.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    write_post(None)
