@AGENTS.md

## Claude Code

- A hook in `.claude/settings.json` runs `uv run ruff format` after every edit, so you don't need to format files yourself.
- `.claude/settings.json` lets you run `uv run pytest` and `uv run ruff` without asking. Every other command still needs approval.
