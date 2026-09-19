# Demo Instructions for This Webinar

**If your working folder is a numbered demo folder, such as `demos/01-copilot-agent-mode`, ignore this file.** It's written for the people and agents who maintain this webinar repository, not for anyone working through a demo. Follow only the instructions inside your demo folder.

The general rules for demos, including folder naming, `uv` setup, the README structure, and the writing style, are in the `CLAUDE.md` file at the root of the repo. This file adds what's specific to this webinar.

## Tools

- **GitHub Copilot in Visual Studio Code**, in the **Copilot** harness (Session Target **Copilot** in the Chat view), the default since VS Code 1.143. Don't write steps for the older **Local** harness, which VS Code is retiring. The demos use the **Ask** agent for questions, **Plan** for a plan (the **Review Plan** card, **Submit Feedback**, and **Implement Plan**), and **Agent** for making a change, with the permissions picker on **Manual permissions**. The Copilot harness saves edits to disk as it goes, runs commands in its own shell, and has **Restore Checkpoint**, but per-change **Keep** and **Undo** aren't in stable VS Code yet.
- **Claude Code in Anthropic's VS Code extension**, not the CLI and not the **Claude** session target in Copilot's Chat view. The walkthroughs use the extension's mode names (**Manual**, **Edit automatically**, **Plan**), its approval labels (**Yes, and don't ask again**, **Yes, and manually approve edits**, **Send feedback and keep planning**), and its rewind option (**Rewind code to here**). The extension starts in **Auto** unless `claudeCode.initialPermissionMode` is set, so every walkthrough switches to **Manual** first.
- Demo 1 uses Copilot only, Demo 2 uses Claude Code only, and Demos 3 and 4 use both. When a step's wording depends on a tool's UI, check it against the current docs for that tool before changing it.
- Python 3.14 for everything. Each demo pins it in `pyproject.toml` (`requires-python = "==3.14.*"`) and `.python-version`, and sets `package = false` so Roombook runs in place.
- Every dependency is pinned to an exact version: `fastapi`, `uvicorn`, and `tzdata` (Windows has no time zone database of its own), with `httpx2`, `pytest`, and `pytest-cov` in the `dev` group. Demo 4 adds `ruff`. Starlette's test client warns about plain `httpx`, which is why the demos use `httpx2`.
- All Python is formatted with `ruff format` at a line length of 100, including in Demos 1 to 3, so that Demo 4's formatting hook only touches new edits. The sample data tables in `roombook/seed.py` sit between `# fmt: off` and `# fmt: on`, one row per line.

## The Codebase

Every demo works on Roombook, a FastAPI and SQLite API for booking meeting rooms in Amsterdam (`Europe/Amsterdam`) and New York (`America/New_York`). Times are stored in UTC and sent and shown in office time. The code is modern and typed, with comments that explain why. The sample data is fixed, with no randomness, so every machine gets the same results, and `roombook/settings.py` pins the app's clock to Monday 26 October 2026 so the sample bookings never fall into the past.

Each demo folder holds its own copy of Roombook at the state the previous demo leaves it in:

| Demo | Folder | Starts with |
|------|--------|-------------|
| 1 | `01-copilot-agent-mode` | Roombook as written, with 14 tests and no agent instruction files |
| 2 | `02-claude-code` | Demo 1's `GET /rooms/available` and its tests (19 tests) |
| 3 | `03-debug-and-refactor` | Demo 2's reviewed `CLAUDE.md`, `tests/test_policies.py`, extra booking-route tests, and a bug report in `issues/` (47 tests) |
| 4 | `04-team-feature` | Demo 3's fix and regression tests, `roombook/slots.py`, `ruff`, the shared settings with the format hook and the test-protection hook (`.claude/hooks/protect_tests.py`), and the spec in `docs/specs/` (55 tests) |

`demos/reference/04-team-feature` is the finished Demo 4, with `AGENTS.md` and the recurring-bookings feature (62 tests). `demos/reference/review-exercise/issue-42-agent-fix.diff` is a deliberately wrong fix for Demo 3's bug, for the review step. It applies to Demo 3's starting code and its tests pass, so regenerate it if Demo 3's `schedule.py` or `tests/test_offices.py` changes.

Some files in Demos 1 to 3 carry problems on purpose, because a later demo deals with them. The presenter's teaching guide lists each one and the demo that resolves it. Copilot loads this file into demo sessions despite the note at the top, so the files and the problems aren't named here. Before changing a demo's code, check the teaching guide, and carry every deliberate problem forward unchanged until the demo that resolves it. Don't describe a problem in any file the agents read in that demo, such as code comments, `CLAUDE.md`, test names, or `pyproject.toml`. The walkthrough `README.md` is the exception, because it has to tell people what to look for.

A change to Roombook or its sample data has to be carried forward through every later demo and the reference folder. Then check the numbers the READMEs quote, such as the test counts, the 27 bookings, and the coverage figures.

## Keeping the Agents to the Demo

Both agents read more than the code, so every demo is set up to give them the demo's context and nothing else:

- Each demo's `.claude/settings.json` has a `claudeMdExcludes` setting with the patterns `**/!(0[1-4]-*)/CLAUDE.md` and `**/!(0[1-4]-*)/AGENTS.md`. Claude Code loads these files from every parent folder, so without it, this file and the root `CLAUDE.md` and `AGENTS.md` would load into every demo session. The patterns skip any such file that isn't inside a numbered folder. That's why the reference copy of Demo 4 is also named `04-team-feature`, and why a new demo folder must keep the two-digit prefix. A fifth demo needs `0[1-5]` in every pattern.
- Copilot loads every `AGENTS.md` and `CLAUDE.md` from the git root down to the session's folder, and there's no setting that excludes one. That's why this file, the root `CLAUDE.md`, and the root `AGENTS.md` each open with a note telling agents in a numbered demo folder to ignore them. Keep that note at the top of all three, and keep anything that would give away a demo's answer out of them.
- The same settings file denies `Read(./README.md)`, so Claude can't read the walkthrough. From Demo 3 on, `CLAUDE.md` also says the README is for people, which covers Copilot.
- Nothing that answers a demo's exercise goes inside that demo's folder. The finished feature lives in `demos/reference/`.
- `pyproject.toml` descriptions and file names in a demo folder mustn't hint at a problem the demo asks the agent to find.

## Outside Services

GitHub Copilot and Claude Code are the only services a demo may use beyond the presenter's machine. Everything else runs locally and offline once `uv sync` has run.

## Coverage

Between them, the demos cover the agenda in the repo `README.md`:

- **From suggestions to agents.** Demo 1 contrasts inline and next edit suggestions, which miss a caller in another file, with an agent that gathers context, edits several files, and runs the tests.
- **How Copilot agent mode works.** Demo 1: gathering context from the workspace, multi-file edits reviewed in one diff, commands approved with **Allow**, iteration on a failing test, and **Restore Checkpoint**. Demo 3 adds planning with the **Plan** agent.
- **How Claude Code works.** Demo 2: search and read tool calls, a subagent that explores in its own context window, `/context`, `/init` and a reviewed `CLAUDE.md`, Manual and Edit automatically, approvals saved for this project (just you) in `.claude/settings.local.json`, and rewinding a change.
- **Practical patterns.** Demo 2: test generation. Demo 3: a debugging session and a refactor. Demo 4: a new feature built from a spec.
- **Keeping agents on track.** Demo 3: prompts that ask for reproduction and evidence before a fix, a live review of a wrong fix whose tests pass, and a plan read for behavior changes. Demo 4: a structured spec, both agents' plans compared side by side, comments on the plan, a deliberate stop and redirect, and reviewing with tests, the diff, and a second agent.
- **Team adoption.** Demo 2: personal versus shared settings. Demo 4: a hook that blocks edits to existing tests on demand, one `AGENTS.md` for both tools, checked-in permissions, and a hook that enforces formatting. `docs/starter-kit/` packages the same setup for attendees' own repositories. Cost and security are covered in the slides.
