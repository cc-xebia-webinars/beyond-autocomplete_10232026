# Demo 2: Context, Tools, and Approvals

In this demo you'll work on Roombook with Claude Code in its VS Code extension. You'll watch Claude gather its own context with search and read tools, turn what it learns into a `CLAUDE.md` file that every future session loads, and then generate tests for the booking rules while you approve its edits and commands. Along the way you'll see the permission modes, how to rewind a change, and where your approvals are saved.

## Before You Start

You'll need these installed:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.11 or later
- [Visual Studio Code](https://code.visualstudio.com/) with the [Claude Code extension](https://code.claude.com/docs/en/vs-code), signed in with a Claude Pro, Max, Team, or Enterprise plan or a Claude Console account

Open this folder as its own VS Code window. If VS Code asks whether you trust the authors of the files in this folder, select **Yes, I trust the authors**, because the Claude Code extension doesn't run in Restricted Mode. Then open a terminal in the folder and install the dependencies:

```
uv sync
```

## What's in This Folder

| File | Purpose |
|------|---------|
| `roombook/` | The Roombook API, with Demo 1's `GET /rooms/available` added |
| `roombook/policies.py` | The booking rules, which you'll write tests for |
| `tests/` | The 19 tests Roombook has so far |
| `.claude/settings.json` | Project settings for Claude Code, shared by everyone who clones the repo |

## Presentation Trail

### Part 1: How Claude gathers context

#### Step 1: Open Claude Code and switch to Manual

Open any file, then select the Claude Code icon (the spark) in the editor toolbar to open the panel. At the bottom of the prompt box is the mode indicator. Unless you've set `claudeCode.initialPermissionMode` as the [demos README](../README.md#claude-code-use-the-extension-panel) describes, a new conversation may start in **Auto**. Select the indicator and choose **Manual**, so Claude asks before it edits a file or runs a command that could change something. You'll try the other modes later.

#### Step 2: Read the project settings

Open `.claude/settings.json`. It holds two settings that keep this demo honest:

- `claudeMdExcludes` lists files Claude shouldn't load. Claude Code reads `CLAUDE.md` from the folder it's working in and from every folder above it, and this repository has `CLAUDE.md` and `AGENTS.md` files of its own, written for the people who maintain the webinar. The two patterns skip any of those files that aren't inside a numbered demo folder. In a monorepo you'd use the same setting to keep another team's instructions out of your sessions.
- The `deny` rule stops Claude from reading this README, which describes what Claude is supposed to find.

#### Step 3: Ask Claude to trace a request

Send this prompt:

```text
Trace what happens when a client calls POST /bookings, from the route to the database. Name the file and function for each step, and list everything that can reject a booking.
```

Watch the tool calls in the panel. Claude searches for files, searches inside them, and reads the ones that matter, much as you would in a codebase you'd never seen. You didn't point it at anything. Reading files doesn't change anything, so Claude doesn't need to ask first, even in Manual mode. Check its answer against `roombook/routes/bookings.py`.

#### Step 4: Look at what's in the context window

```text
/context
```

Claude shows how its context window is being used: the system prompt, its tools, any memory files, and the conversation so far. There are no memory files yet, because this folder has no `CLAUDE.md`. Note how much the conversation is using.

#### Step 5: Explore with a subagent

On a large codebase, reading everything into one conversation fills the context window fast. Send this prompt:

```text
Use a subagent to find every place in roombook/ that reads or writes the bookings table. Report back a short list with the file and function for each.
```

Claude hands the search to a subagent, which reads files in a context window of its own and sends back only its summary. Expand the subagent's step in the panel to see how many searches and reads it made, then run `/context` again. The conversation grew by the size of the summary, not by every file the subagent read. On a codebase this small the saving is modest. On a large one, it's the difference between finishing a task and running out of context halfway through.

### Part 2: Project memory

#### Step 6: Generate a CLAUDE.md

```text
/init
```

Claude explores the project and proposes a `CLAUDE.md`. In Manual mode you see the file as a diff before it's written. Accept it.

#### Step 7: Review and trim it

Open `CLAUDE.md` and edit it the way you'd review a teammate's document. Keep the commands, the layout, and the conventions someone new would get wrong, such as times being stored in UTC but sent in office time. Remove generic advice that applies to any project. Then add the rules Claude can't work out from the code:

```markdown
## Rules

- Don't edit an existing test to make code pass. If a test looks wrong, stop and explain why.
- Ask before adding a dependency, and add it with `uv add`, never `pip install`.
- For existing behavior, expected values in tests come from running the code. For new behavior, they come from the spec. Never work them out by hand.
- Keep each change small, and run `uv run pytest` after it.
```

Every line in `CLAUDE.md` is loaded at the start of every new session in this folder, so shorter and more specific is better. Our reviewed version is [Demo 3's CLAUDE.md](../03-debug-and-refactor/CLAUDE.md).

### Part 3: Test generation, with approvals

#### Step 8: Check coverage first

```
uv run pytest --cov --cov-report=term-missing
```

`roombook/policies.py` is at 71%. The API tests reach some of the rules, but the edges, such as a booking that's exactly four hours long, aren't tested anywhere.

#### Step 9: Ask for tests

Send this prompt:

```text
Write tests for roombook/policies.py in a new file, tests/test_policies.py. Cover every rule and its edges, such as exactly four hours, the opening and closing times, and exactly 90 days ahead. Get each expected value by running the code, not by working it out. Don't change anything under roombook/.
```

#### Step 10: Approve edits and commands

Claude stops at each step that changes something. For a file edit, you see the diff and can accept it, reject it, or tell Claude what to do instead. For a command, such as `uv run pytest`, read it before you allow it. When Claude asks to run `uv run pytest`, choose **Yes, and don't ask again**, and set where to save the rule to **this project (just you)**.

#### Step 11: Switch to Edit automatically

Once you trust the direction, open the mode indicator and choose **Edit automatically**. Edits now go through without a prompt, and so do simple file commands such as creating a folder. Other commands still ask, unless you've already allowed them. This is a good balance when a fast test suite is checking every change.

#### Step 12: Check coverage again

```
uv run pytest --cov --cov-report=term-missing
```

`roombook/policies.py` should now be at or near 100%.

### Part 4: Review and permissions

#### Step 13: Read the tests

Open `tests/test_policies.py`. Look for test names that say which rule they check, exact boundary values rather than comfortable middles, and a fixed clock rather than the real time. Be wary of any test that copies the implementation's arithmetic, because it can't catch a mistake in it. Our version is [Demo 3's test_policies.py](../03-debug-and-refactor/tests/test_policies.py).

#### Step 14: Rewind a change

Ask Claude for a small change you can throw away:

```text
Add a one-line docstring to every test in tests/test_policies.py.
```

When it's done, hover over that message in the panel, select the rewind button, and choose **Rewind code to here**. The test file goes back to how it was before the message. Rewinding restores the files Claude has edited. A file that only a terminal command changed isn't tracked, so rewinding leaves it as it is.

#### Step 15: See where your approval went

Open `.claude/settings.local.json`. The rule you saved for **this project (just you)** in Step 10 is here, in the personal settings file that git ignores, so it applies only to you. Choosing **this project (shared)** would have saved it to `.claude/settings.json` instead, which is checked in, so the whole team gets the rule. [Demo 4's settings.json](../04-team-feature/.claude/settings.json) holds rules like that.

## What You Saw

- Claude Code gathers its own context with search and read tools, and `/context` shows what's using its context window. A subagent explores in a context window of its own and reports back only what you need.
- `/init` gives you a first draft of `CLAUDE.md`, and reviewing it is where the value is: keep what's specific, cut what's generic, and add the rules the code can't tell it.
- In Manual mode you approve every edit and every command that could change something. Edit automatically lets edits flow and still asks before most commands.
- Rewinding undoes a change you don't want, and the rules you approve can be personal or shared with the team.
