"""Format only the file the agent just edited.

Claude Code runs this after every edit or write (see .claude/settings.json) and passes the tool
call as JSON on stdin. Formatting just that file, rather than the whole repository, keeps an
existing codebase's unformatted files out of the agent's diff.
"""

import json
import subprocess
import sys

# Change this to match your formatter, such as ["npx", "prettier", "--write"].
FORMATTER = [sys.executable, "-m", "ruff", "format", "--quiet"]
EXTENSIONS = (".py",)


def main() -> int:
    call = json.load(sys.stdin)
    path = call.get("tool_input", {}).get("file_path")
    if isinstance(path, str) and path.endswith(EXTENSIONS):
        # A formatting failure shouldn't block the agent, so the result is ignored.
        subprocess.run([*FORMATTER, path], check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
