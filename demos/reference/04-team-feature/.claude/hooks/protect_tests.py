"""Refuse edits to test files that are already in git.

The rule "don't edit a test to make code pass" is written in CLAUDE.md, but an instruction is
only a request. This hook makes it a rule: Claude Code runs it before every edit or write (see
.claude/settings.json), and exit code 2 blocks the edit and sends the message on stderr back to
the agent, so it can change course. New test files aren't in git yet, so the agent can still
create and edit tests of its own.

It covers the agent's file-editing tools, not every shell command, and it can only protect files
that git tracks. Keep running the tests in CI as the final safeguard.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def edited_path(call: dict) -> str | None:
    # Claude Code sends tool_input.file_path. Other agents that read this file may use other
    # field names, so look in the usual places rather than assuming one shape.
    for key in ("tool_input", "toolArgs", "tool_args"):
        args = call.get(key)
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except ValueError:
                continue
        if isinstance(args, dict):
            for name in ("file_path", "filePath", "path"):
                if isinstance(args.get(name), str):
                    return args[name]
    return None


def main() -> int:
    call = json.load(sys.stdin)
    path = edited_path(call)
    if path is None:
        return 0
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or call.get("cwd") or os.getcwd())
    target = (project / path).resolve()
    try:
        relative = target.relative_to(project.resolve())
    except ValueError:
        return 0
    if relative.parts[:1] != ("tests",):
        return 0
    # A non-zero exit just means git doesn't track the file, so it's a new test.
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", relative.as_posix()],
        cwd=project,
        capture_output=True,
        check=False,
    )
    if tracked.returncode != 0:
        return 0
    print(
        f"{relative.as_posix()} is an existing test, and existing tests are protected in this "
        "project. Don't change a test to make code pass. Fix the code instead, or put new "
        "tests in a new file under tests/. If you think this test is wrong, stop and explain why.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
