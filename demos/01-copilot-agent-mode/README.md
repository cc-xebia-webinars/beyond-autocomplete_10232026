# Demo 1: From Autocomplete to Agent

In this demo you'll meet Roombook, a small API for booking meeting rooms in an Amsterdam office and a New York office, and you'll work on it with GitHub Copilot in two very different ways. First you'll use inline suggestions, where Copilot completes what you're typing and you drive every step. Then you'll hand Copilot's agent a whole feature and watch it find its way around the code, edit several files, run the tests, and fix what fails. The point is to see what changes when the assistant can act, and what you need to watch when it does.

## Before You Start

You'll need these installed:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.11 or later
- [Visual Studio Code](https://code.visualstudio.com/) with [GitHub Copilot set up](https://code.visualstudio.com/docs/setup/copilot)

Open this folder as its own VS Code window, open a terminal in it, and install the dependencies:

```
uv sync
```

In the Chat view, start a **New Chat** with **Session Target** set to **Copilot**. The [demos README](../README.md#copilot-use-the-copilot-harness) explains how.

## What's in This Folder

| File | Purpose |
|------|---------|
| `roombook/main.py` | Builds the FastAPI app and seeds the sample database on first start |
| `roombook/routes/` | The API: `rooms.py`, `bookings.py`, and `offices.py` |
| `roombook/policies.py` | The booking rules, such as opening hours and the 4-hour limit |
| `roombook/availability.py` | Finds the bookings that clash with a time window |
| `roombook/timeutils.py` | Converts between office time and the UTC times in the database |
| `roombook/seed.py` | The sample rooms and bookings |
| `tests/` | API tests, each with its own freshly seeded database |
| `.claude/settings.json` | Settings for Claude Code, which Demo 2 explains. This demo doesn't use them |

## Presentation Trail

### Part 1: Meet Roombook

#### Step 1: Run the tests

```
uv run pytest
```

All 14 tests pass. Each one gets a freshly seeded database and a clock pinned to Monday 26 October 2026, which you can see in `tests/conftest.py`.

#### Step 2: Start the API

```
uv run uvicorn roombook.main:app --reload
```

Open http://127.0.0.1:8000/docs. The first start builds the sample database in the `data` folder: eleven rooms and two weeks of bookings. Try **GET /offices/{code}/schedule** with the code `AMS` and the date `2026-10-27` to see a day in the Amsterdam office. Every time in the API is local to the office, so a 09:00 meeting in New York is sent and shown as `09:00`, and `roombook/timeutils.py` converts it to UTC for storage. Leave the server running, and open a second terminal for the next steps.

#### Step 3: Read how a booking is made

Open `roombook/routes/bookings.py` and read `create_booking`. It looks up the room, attaches the office's time zone to the requested times, checks them against the rules in `roombook/policies.py`, asks `roombook/availability.py` for clashing bookings, and saves the booking. Then open `roombook/availability.py`. Its one function, `conflicts`, finds the bookings that overlap a window. A booking that ends at 10:00 doesn't clash with one that starts at 10:00.

### Part 2: Inline suggestions

#### Step 4: Let Copilot finish a function

At the bottom of `roombook/availability.py`, type this signature and docstring, then pause:

```python
def has_equipment(room: sqlite3.Row, required: list[str]) -> bool:
    """True if the room has every item in required."""
```

Copilot suggests a body in grey text. Press Tab to accept it. Look at what it had to work with: your signature, your docstring, and the code around the cursor. Does its answer cope with a room whose equipment is an empty string? It can only know that the database stores equipment as comma-separated text if that's visible to it.

#### Step 5: Accept a next edit suggestion

In the same file, rename the `ignore_booking_id` parameter of `conflicts` to `exclude_booking_id`. Copilot notices that the function body still uses the old name and shows an arrow in the gutter. Press Tab to jump to the suggested edit, and Tab again to accept it. Then run the tests:

```
uv run pytest
```

One test fails, because `move_booking` in `roombook/routes/bookings.py` still passes `ignore_booking_id`. Suggestions work where you're looking, and nothing searched the rest of the codebase for callers. For a rename you'd normally use **Rename Symbol** (F2), which does update every caller. The point is what a suggestion can see: the code around your cursor, not the code that depends on it. Press Ctrl+Z (Cmd+Z on macOS) in `availability.py` until the parameter is called `ignore_booking_id` again, and run the tests once more to see all 14 pass.

### Part 3: The agent

#### Step 6: Start an agent session

Select **New Chat**, check that **Session Target** is **Copilot**, and pick **Agent** in the agent picker. Leave the permissions picker on **Manual permissions**, so Copilot asks before it runs a command that could change something.

#### Step 7: Ask for a feature

Send this prompt:

```text
Add an endpoint, GET /rooms/available, that lists the rooms in an office that are free for a whole time window. It takes an office code, a local start and end time like POST /bookings, an optional minimum capacity, and optional required equipment that can be given more than once. Reuse the existing clash check. Add tests to tests/test_rooms.py, and run the test suite until it passes.
```

#### Step 8: Watch it gather context

Before it edits anything, Copilot searches the workspace and reads files. Each search, read, and edit appears in the chat as a tool call that you can expand to see the details. Notice that you didn't tell it where the routes, models, or tests live.

#### Step 9: Approve the commands

When Copilot wants to run a command, such as `uv run pytest`, it shows the command and waits. Read it, then select **Allow**. The options include allowing a command for the rest of the session, but allow it once each time here, so you see every run. Copilot runs commands in its own shell rather than in a VS Code terminal, so expand the command in the chat to see the output it saw. Approving each command is your main control over an agent that can run them.

#### Step 10: Watch it iterate

If a test fails, Copilot reads the output, works out why, changes the code, and runs the tests again. Expand the failing run in the chat and read the error yourself before Copilot explains it: you'll be reviewing its reasoning, so it helps to have your own. If everything passes the first time, there's nothing to fix, which is fine. Either way, count how many times it ran the tests before it was done.

### Part 4: Review

#### Step 11: Review each change

Copilot saved its edits as it went. Select the changed-files summary above the chat input to see every change in one multi-file diff, and read each one. Check where the new route sits in `roombook/routes/rooms.py`, whether it reused `conflicts` as you asked, and whether the new tests check the filters or only that the endpoint answers. To throw away the changes to one file, use **Discard Changes** on it in the Source Control view.

#### Step 12: Restore a checkpoint

Hover over your request in the chat, select **Restore Checkpoint**, and confirm. The workspace goes back to how it was before the request, which is how you'd throw away a run that went the wrong way. Select **Redo** to bring the changes back. Restoring a checkpoint undoes Copilot's file edits, not the effects of commands it ran.

#### Step 13: Check the result yourself

Run the tests:

```
uv run pytest
```

Then go back to http://127.0.0.1:8000/docs, which has reloaded with your changes, and try **GET /rooms/available** with the office `NYC`, a start of `2026-10-27T14:00`, an end of `2026-10-27T15:00`, and a minimum capacity of `6`. Demo 2 starts from our reviewed version of this feature, so you can compare it with what Copilot wrote for you in [Demo 2's rooms.py](../02-claude-code/roombook/routes/rooms.py).

## What You Saw

- Inline suggestions complete the code in front of you. They're fast, and you stay in control of every step, but they don't look for the other places a change affects.
- The agent takes a goal, gathers its own context, edits several files, runs commands, and iterates on failures.
- Approving commands and reviewing the diff are where you stay in the loop. Checkpoints let you throw away a run and try again.
- The agent's tests deserve the same review as its code, because they're what it uses to decide it's done.
