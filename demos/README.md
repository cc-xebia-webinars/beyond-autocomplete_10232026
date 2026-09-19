# Demos

These four demos follow one codebase, Roombook, a small FastAPI service for booking meeting rooms in an Amsterdam office and a New York office. Demo 1 uses GitHub Copilot's agent, Demo 2 uses Claude Code, and Demos 3 and 4 use both, side by side. Each demo starts where the previous one leaves off, and each is self-contained, with its own copy of the code and its own `uv` project pinned to Python 3.14, so you can run any of them on its own.

| # | Demo | Description | Time |
|---|------|-------------|------|
| 1 | [From Autocomplete to Agent](./01-copilot-agent-mode/README.md) | Inline suggestions and next edit suggestions, then a whole feature built by Copilot's agent: planning, edits across several files, approved terminal commands, iteration on failing tests, and review with checkpoints. | 17 min |
| 2 | [Context, Tools, and Approvals](./02-claude-code/README.md) | Claude Code gathers its own context, explores with a subagent, turns what it learns into a reviewed `CLAUDE.md`, and generates tests for the booking rules while you approve edits and commands, switch permission modes, and rewind a change. | 17 min |
| 3 | [Debug and Refactor with Agents](./03-debug-and-refactor/README.md) | A debugging session in Claude Code that reproduces a time zone bug before fixing its root cause, and a refactor in Copilot that's planned, reviewed for behavior changes, and checked by unchanged tests. | 18 min |
| 4 | [Ship a Feature and Keep It on Track](./04-team-feature/README.md) | A hook that stops Claude from changing existing tests, one `AGENTS.md` for both tools, and a feature built from a written spec: both agents plan it side by side, Claude builds it while you steer, and Copilot gives a second opinion. | 18 min |

## Getting Ready

Every demo needs these tools:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.11 or later. It installs Python 3.14 for you if you don't have it.
- [Visual Studio Code](https://code.visualstudio.com/) with [GitHub Copilot set up](https://code.visualstudio.com/docs/setup/copilot). Copilot Free includes the agent, with monthly limits.
- The [Claude Code extension](https://code.claude.com/docs/en/vs-code) for VS Code, for Demos 2 to 4. Sign in with a Claude Pro, Max, Team, or Enterprise plan, or a Claude Console account.

Run `uv sync` in each demo folder while you're online. After that, everything runs offline except Copilot and Claude Code themselves.

Open each demo as its own VS Code window, for example `code demos/02-claude-code`. On macOS, install the `code` command first: open the Command Palette and run **Shell Command: Install 'code' and optionally 'copilot' commands in PATH**, and decline the optional Copilot command if you don't need it. Opening the demo folder directly keeps each agent working on that demo's code. If VS Code asks whether you trust the authors of the files in the folder, select **Yes, I trust the authors**. The Claude Code extension doesn't run in VS Code's Restricted Mode, and Claude Code only applies a folder's allow rules once the folder is trusted.

### Copilot: Use the Copilot Harness

VS Code can run a chat on several agent harnesses, chosen with the **Session Target** control in the Chat view. The demos use **Copilot**, which has been the default since VS Code 1.143. VS Code is retiring its older **Local** harness, so the walkthroughs don't use it.

1. Select **New Chat** (**+**) at the top of the Chat view.
2. Check that **Session Target** is **Copilot** before you send the first prompt. You can't change the harness once a session has started.
3. Pick an agent in the agent picker: **Ask** for questions, which never changes files, **Plan** for a plan before any code, or **Agent** to make a change.
4. Leave the permissions picker on **Manual permissions**, so Copilot asks before it runs a command that could change something. Common read-only commands run without asking.

Copilot saves its edits to disk as it works. To read them, open the changed-files summary above the chat input, which shows every change in one diff. To go back, hover over an earlier request and select **Restore Checkpoint**.

Copilot also reads instruction files, such as `AGENTS.md` and `CLAUDE.md`, in every folder from the repository root down to the folder you opened. This repository's top-level instruction files are for the people who maintain it, and each one opens with a note telling agents in a demo folder to ignore it.

### Claude Code: Use the Extension Panel

The demos use Anthropic's Claude Code extension. To open it, open any file and select the Claude Code icon (the spark) in the editor toolbar. The mode indicator at the bottom of the prompt box switches between **Manual**, where Claude asks before it edits a file or runs a command that could change something, **Edit automatically**, **Plan**, and **Auto**.

Recent versions start new conversations in **Auto** wherever your account offers it, and in Auto a classifier decides which actions Claude can take without asking. The demos start in **Manual** so you see every step. To make every new conversation start there, add this line to your VS Code user settings (JSON):

```json
"claudeCode.initialPermissionMode": "manual"
```

VS Code's Chat view also offers a **Claude** session target. That's a different integration, billed through a paid Copilot plan or your own Anthropic API key, with its own settings. The steps in these demos are written for the Claude Code extension.

### Tested Versions

The walkthroughs were last checked in October 2026 with VS Code 1.143, the Claude Code extension 2.1.310, GitHub Copilot in VS Code's Copilot harness, and uv 0.13.5. Both agents' interfaces change often. If a button or menu doesn't match a walkthrough, check the tool's own documentation for its current name, and carry on with the step.

## The Sample Data

Each demo builds a small SQLite database in its `data` folder the first time the API starts. It holds eleven rooms and 27 bookings in late October and early November 2026, across both offices' clock changes. It's never committed. To rebuild it, run this from the demo's folder:

```
uv run python -m roombook.seed --reset
```

The app's clock is pinned to Monday 26 October 2026, so the sample bookings stay in the future whenever you run the demos. `roombook/settings.py` explains how to change it. The tests use their own temporary databases, so running them never touches the sample data.

## The Agents' Answers Will Vary

Copilot and Claude won't write the same code, tests, or plans for you that they wrote for us, so the walkthroughs tell you what to look for rather than what to expect word for word. Each demo starts from a finished, reviewed version of the previous demo's work, and the [reference folder](./reference/README.md) holds a finished version of Demo 4. It sits outside the demo folders on purpose, so neither agent can find the answer while it's working.

## Using Another AI Tool

The workflow doesn't depend on these two tools. `AGENTS.md`, which Demo 4 creates, is read by many coding agents, including [Copilot](https://code.visualstudio.com/docs/agent-customization/custom-instructions), [Cursor](https://cursor.com/docs/rules), and OpenAI Codex, and the prompts in each walkthrough are plain text you can paste into any agent's chat.
