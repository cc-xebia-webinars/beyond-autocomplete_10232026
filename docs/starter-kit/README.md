# Agent Starter Kit

These files are a starting point for setting up your own repository for coding agents, based on what the webinar's demos built. Copy them in, replace the parts in angle brackets, and review them with your team like any other code. Keep every file short: agents load the instructions into every session, and so do the people who maintain them.

| File | Copy it to | What it does |
|------|-----------|--------------|
| [AGENTS.md](./AGENTS.md) | `AGENTS.md` at the root of your repository | The project instructions that Copilot, Claude Code, Cursor, OpenAI Codex, and most other agents read |
| [CLAUDE.md](./CLAUDE.md) | `CLAUDE.md` next to `AGENTS.md` | Imports `AGENTS.md` for Claude Code, plus anything only Claude needs |
| [claude-settings.json](./claude-settings.json) | `.claude/settings.json` | Shared Claude Code permissions and two hooks: one formats each edited file, and one protects existing tests |
| [format_edited.py](./format_edited.py) | `.claude/hooks/format_edited.py` | The hook that formats only the file the agent just edited, so the rest of the codebase stays out of the diff |
| [protect_tests.py](./protect_tests.py) | `.claude/hooks/protect_tests.py` | The hook that refuses edits to test files git already tracks |
| [spec-template.md](./spec-template.md) | Wherever your team keeps specs | A short spec for a feature, written for the agent as much as for people |

## Adapting the Settings

- The settings assume a Python project run with `uv`, tests in `tests/`, and Ruff for formatting. Change the commands in the `allow` list, and the formatter at the top of `format_edited.py`, to the ones your project uses, such as `npm test` or Prettier.
- Each allow and deny rule appears twice, once for Bash and once for PowerShell, because Claude Code runs commands through one or the other depending on the machine.
- Claude Code only applies the allow rules once the folder is trusted. Deny rules and hooks apply straight away.
- Hooks are configured per tool. These are Claude Code hooks, so check how each other agent your team uses enforces the same rules.
- A hook covers the actions it's written for. The test hook stops Claude's edit tools, not every shell command, and it only protects files git tracks. Keep running the tests in CI as the final safeguard.

## Before You Rely on It

- Ask an agent to break each rule on purpose, such as editing an existing test or running `git push`, and confirm it's stopped.
- Ask each agent you use which instruction files it loaded, and check that it found `AGENTS.md`.
- Revisit `AGENTS.md` whenever an agent session teaches you something, such as a convention it got wrong. Add the lesson in one line.

The [Agentic Coding Checklist](../agentic-coding-checklist.md) covers the rest of the workflow, from preparing a task to reviewing the result.
