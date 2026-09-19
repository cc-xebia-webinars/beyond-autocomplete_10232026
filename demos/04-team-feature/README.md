# Demo 4: Ship a Feature and Keep It on Track

In this demo you'll build a new feature, weekly recurring bookings, the way a team would. First you'll look at the guardrails the project shares, including a hook that stops Claude from changing an existing test, and you'll set things up so Claude Code and Copilot read the same instructions. Then you'll give both agents the same written spec, compare their plans side by side, and have Claude build the feature while you step in to steer it. You'll finish by reviewing the result with tests, the diff, and a second opinion from Copilot.

## Before You Start

You'll need these installed:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.11 or later
- [Visual Studio Code](https://code.visualstudio.com/) with [GitHub Copilot set up](https://code.visualstudio.com/docs/setup/copilot)
- The [Claude Code extension](https://code.claude.com/docs/en/vs-code) for VS Code, signed in with a Claude Pro, Max, Team, or Enterprise plan or a Claude Console account

Open this folder as its own VS Code window, and trust it if VS Code asks. Claude Code only applies the allow rules in `.claude/settings.json` in a trusted workspace. Open a terminal in the folder and install the dependencies, which now include the Ruff formatter:

```
uv sync
```

## What's in This Folder

| File | Purpose |
|------|---------|
| `roombook/` | The Roombook API, with Demo 3's fix and refactor (`roombook/slots.py`) |
| `CLAUDE.md` | The project memory, with the lesson from Demo 3's debugging session |
| `.claude/settings.json` | Shared permissions and two hooks for Claude Code |
| `.claude/hooks/protect_tests.py` | The hook that refuses edits to existing tests |
| `docs/specs/recurring-bookings.md` | The spec for the feature you'll build |
| `tests/` | 55 tests, including the regression tests from Demo 3 |

## Presentation Trail

### Part 1: Guardrails and context the whole team shares

#### Step 1: Read the shared settings

Open `.claude/settings.json`. It's checked in, so everyone who clones the repo gets the same setup:

- `allow` lets Claude run `uv run pytest` and `uv run ruff` without asking. Each rule appears twice because Claude Code runs commands through Bash or PowerShell, depending on the machine, and a rule names the tool it applies to.
- `deny` blocks `git push`, so publishing stays a person's decision, and it stops Claude from reading this README.
- The `PreToolUse` hook runs `.claude/hooks/protect_tests.py` before every edit. If the file being edited is a test that git already tracks, the hook refuses the edit and tells Claude why. New test files are fine.
- The `PostToolUse` hook runs `uv run ruff format` after every edit, so formatting never shows up in review.

`CLAUDE.md` already says not to edit a test to make code pass, but an instruction is only a request. A hook runs every time. It has limits, though: it covers Claude's file-editing tools, so a shell command could still change a test, and it can only protect files that git tracks. That's why running the tests in CI stays the final safeguard.

#### Step 2: Try to break the rule on purpose

Open the Claude Code panel, set the mode to **Manual**, and send this prompt:

```text
The test that rejects bookings that don't start on the quarter hour, in tests/test_policies.py, is too strict. Loosen it so any start minute is accepted.
```

When Claude tries to edit the test, the hook blocks it, and Claude reads the hook's message and explains what happened instead. If it offers to change the rule in `roombook/policies.py` instead, reject that edit too: the booking rules belong to the office managers. Every Claude session gets this guardrail, whatever the prompt says.

#### Step 3: Move the shared facts into AGENTS.md

`CLAUDE.md` is Claude Code's file. Copilot happens to read it too, but `AGENTS.md` is the file most coding agents look for, including Cursor and OpenAI Codex. Send this prompt:

```text
Move the project facts in CLAUDE.md into a new AGENTS.md, so Copilot and other tools read the same file. Leave CLAUDE.md with a first line of @AGENTS.md, which imports it, and keep anything else in CLAUDE.md only if it applies to Claude Code alone.
```

Accept the edits. The `@AGENTS.md` line pulls the shared file into every Claude session, so there's one copy to maintain.

### Part 2: One spec, two plans

#### Step 4: Read the spec

Open `docs/specs/recurring-bookings.md`. It's short, and every section is there for the agent as much as for people. The goal says why, the context names the code to reuse, the constraints rule out the shortcuts an agent might take, and the acceptance criteria say exactly what done means. Criterion 1 is the one to watch: a weekly booking at 10:00 has to stay at 10:00 after New York's clocks change on 1 November.

#### Step 5: Ask both agents for a plan

You'll give both agents the same prompt at the same time. Planning doesn't change any files, so they can work side by side.

In the Claude Code panel, start a new conversation, choose **Plan** in the mode indicator, and send the prompt below. Then, in the Chat view, start a **New Chat** with **Session Target** set to **Copilot**, pick **Plan** in the agent picker, and send the same prompt. If either agent asks a clarifying question, answer it.

```text
Read docs/specs/recurring-bookings.md and plan how to implement it.
```

#### Step 6: Compare the two plans

Claude opens its plan as a document. Copilot shows a **Review Plan** card, and **Open Full Plan** shows all of it. Don't try to read both plans end to end. Find the same two things in each:

- **The clock change.** How does each plan work out the date of each occurrence, and would it keep 10:00 at 10:00 after 1 November?
- **The constraints.** Does either plan add a dependency, change `check_slot` or the clash check, or touch existing tests?

If you have more time, also compare which files each one read and which tests each promises. Copilot's plan should follow the commands and conventions in `AGENTS.md`, which shows it's reading the file you just created.

Neither tool is right by default. Comparing plans is a quick, cheap way to see what each one assumed, and it's often where you spot the gap in the plan you're about to approve. Leave Copilot's plan as it is, and don't select **Implement Plan**: Claude builds the feature in this demo.

#### Step 7: Push back on Claude's plan and approve it

Add a comment to Claude's plan wherever it breaks the spec, and wherever Copilot's plan caught something Claude's missed. Then select **Send feedback and keep planning**, and Claude revises the plan.

When the plan matches the spec, approve it with **Yes, and manually approve edits**, then switch the mode indicator to **Edit automatically**, so Claude builds without stopping for each file. The first option, **Yes, and use auto mode**, would hand the approvals to the Auto classifier, and in this demo you want to approve every command that isn't on the allow list yourself.

### Part 3: Build and step in

#### Step 8: Watch it build

Claude works through the plan. `uv run pytest` and `uv run ruff` run without a prompt because of the allow rules, the formatting hook reformats each file as it's written, and the test hook stops any edit to an existing test. Any other command still asks.

#### Step 9: Step in on purpose

You don't have to wait for an agent to finish before you steer it. As soon as Claude's first edit to `roombook/series.py` appears, select **Stop**, and send this prompt:

```text
Before you write any more code, add the test for acceptance criterion 1 to a new test file and run it. Then carry on.
```

Claude picks up where it stopped, with the most important test written first. Watch for the other moments to step in too: an agent that adds a dependency, changes files the spec doesn't mention, or runs the same failing test again and again needs the same treatment. Stop it, and say what you want instead. For a small correction that doesn't need a full stop, type your message while Claude works. It's queued and delivered when Claude finishes its current step.

### Part 4: Review the result

#### Step 10: Run the tests yourself

```
uv run pytest
```

Every test should pass, including the 55 that were there before. Then open the new test file and find the test for criterion 1. Check that it asserts the local times of the occurrences after 1 November, because that's the bug most implementations have.

#### Step 11: Read the diff

Open the **Source Control** view and read the diff one file at a time. Check that the route functions are thin, that the series logic is in `roombook/series.py`, that no existing test changed, and that nothing outside the spec changed.

#### Step 12: Get a second opinion from Copilot

In the Chat view, start a **New Chat** with **Session Target** set to **Copilot**, pick **Ask**, and send this prompt. **Ask** never changes files, which suits a reviewer.

```text
Review the uncommitted changes in this folder against docs/specs/recurring-bookings.md. List anything that doesn't meet the spec, and anything that looks risky.
```

For a general review without the spec, the **Code Review** button in the Source Control view reviews your uncommitted changes and adds its comments to the code.

A second agent has no stake in the first one's choices, which makes it a useful reviewer. It doesn't replace your review, though. Read its findings and decide which ones matter. To compare with a finished version, see the [reference folder](../reference/README.md).

## What You Saw

- A hook enforces a rule in every Claude session, where an instruction in `CLAUDE.md` is only a request. It covers only the actions it's written for, and hooks are configured per tool, so CI stays the backstop, and you should check that each tool you use really enforces your rules.
- `AGENTS.md` gives every tool the same project instructions, and `CLAUDE.md` imports it and adds anything only Claude needs.
- A short spec with constraints and acceptance criteria is the best prompt for a feature. Comparing two agents' plans, and commenting on the one you approve, is the cheapest place to correct course.
- Stepping in on purpose, reading the diff, and asking a second agent are how you keep a capable agent on track.
