# Demo 3: Debug and Refactor with Agents

This demo works through two of the most common engineering tasks with an agent, one with each tool. First you'll take a real bug report to Claude Code and run a debugging session the way a careful engineer would: reproduce the bug with a failing test, find the root cause and the evidence for it, and only then fix it. Then you'll use Copilot to plan and carry out a refactor that removes duplicated code without changing what the code does, with the tests run before and after.

## Before You Start

You'll need these installed:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.11 or later
- [Visual Studio Code](https://code.visualstudio.com/) with [GitHub Copilot set up](https://code.visualstudio.com/docs/setup/copilot)
- The [Claude Code extension](https://code.claude.com/docs/en/vs-code) for VS Code, signed in with a Claude Pro, Max, Team, or Enterprise plan or a Claude Console account

Open this folder as its own VS Code window, and trust it if VS Code asks. Open a terminal in it and install the dependencies:

```
uv sync
```

## What's in This Folder

| File | Purpose |
|------|---------|
| `roombook/` | The Roombook API, as Demo 2 left it |
| `CLAUDE.md` | The reviewed project memory from Demo 2. Copilot reads it too |
| `tests/test_policies.py` | The reviewed booking-rule tests from Demo 2 |
| `issues/0042-nyc-schedule-missing-evening-bookings.md` | A bug report from the New York office |
| `.claude/settings.json` | Project settings for Claude Code, explained in Demo 2 |

## Presentation Trail

### Part 1: A debugging session with Claude Code

#### Step 1: Read the bug report

Open `issues/0042-nyc-schedule-missing-evening-bookings.md`. An evening booking in New York appears on the following day's lobby schedule. The report has three clues worth noticing: the start time shown is still correct, a 7:00 pm booking on another day isn't affected, and Amsterdam looks fine.

#### Step 2: Run the tests

```
uv run pytest
```

All 47 tests pass. The bug is real, so the suite has a gap, and the first job is to close it.

#### Step 3: Reproduce it before fixing it

Open the Claude Code panel, set the mode to **Manual**, and send this prompt:

```text
Read issues/0042-nyc-schedule-missing-evening-bookings.md. Reproduce the bug with a failing test before you change any code under roombook/. Run the test to show that it fails, then stop and tell me what you see.
```

Accept the new test and allow `uv run pytest`. A failing test is the best possible start to a debugging session: it proves the bug exists, it tells you when it's fixed, and it stays behind to stop the bug coming back.

#### Step 4: Ask for the root cause and the evidence

```text
Find the root cause. Show me the lines responsible, and explain why the 8:00 pm rehearsal is on the wrong day when the 7:00 pm webinar on Thursday isn't. Don't fix anything yet.
```

A good answer accounts for every clue in the report. Then ask one more question, because a root cause is rarely used in only one place:

```text
What else in the codebase uses that code, and is it affected too?
```

#### Step 5: Fix the cause, not the symptom

```text
First add a failing test for every other place that's affected, and a test that a day in New York on 1 November 2026 is 25 hours long, because that's when the clocks go back. Then fix the root cause, not the symptom, and run the full suite.
```

Read the fix before you accept it. Two fixes look right and aren't. One changes only the lobby schedule and leaves the other code that has the same fault. The other converts the start of the day to UTC and adds 24 hours there, which is wrong on the two days a year when the clocks change. The tests you asked for in this step catch both.

#### Step 6: Review a fix that passes the tests

Another agent session produced its own fix for the same issue, starting from the code as it was before your Step 5. Open [issue-42-agent-fix.diff](../reference/review-exercise/issue-42-agent-fix.diff). The agent's summary at the top says all 48 tests pass, and they do. Before you read on, review it the way you'd review a teammate's pull request, and find what's wrong.

<details>
<summary>What to look for</summary>

- **It fixes the symptom in one place.** `day_bounds` is still wrong, and the fix only adjusts the window in `roombook/schedule.py`. With this fix applied, `GET /rooms/10/bookings?day=2026-10-27` still misses the rehearsal, and the next caller of `day_bounds` gets the bug too.
- **It reads the real clock.** `datetime.now()` gives the office's offset today, not on the day being shown, so the window is an hour off for any date on the other side of a clock change. It also ignores the app's own clock in `roombook/deps.py`. It only passes because opening hours leave room either side of midnight.
- **It documents the bug instead of fixing it.** The new comment describes `day_bounds` returning the UTC day as if that were its job.
- **Its test checks half the story.** It checks that the rehearsal appears on 27 October, but not that it's gone from the 28th, and nothing after 1 November or for the room endpoint.

Passing tests tell you the code does what the tests check, and nothing more. That's why you read the tests in a diff before you read the code.

</details>

#### Step 7: Capture what you learned

```text
Add one line to CLAUDE.md about day boundaries, so the next session doesn't repeat this bug.
```

A lesson that only lives in a chat history is gone when the session ends. [Demo 4's CLAUDE.md](../04-team-feature/CLAUDE.md) has the line we added.

### Part 2: A refactor with Copilot

#### Step 8: Check what the tests cover

```
uv run pytest --cov --cov-report=term-missing
```

Look at `roombook/routes/bookings.py`. It's well covered, including moving a booking onto another one, moving a cancelled booking, and a moved boardroom booking going back to pending. A refactor is only as safe as the tests underneath it, so check this before you change anything.

#### Step 9: Plan the refactor

Open `roombook/routes/bookings.py` and compare `create_booking` with `move_booking`. Both repeat the same checks: the offset check, attaching the time zone, the booking rules, and the clash check. In the Chat view, start a **New Chat** with **Session Target** set to **Copilot**, pick **Plan** in the agent picker, and send this prompt. If Copilot asks a clarifying question first, answer it.

```text
Plan a refactor of roombook/routes/bookings.py. create_booking and move_booking repeat the same checks: the offset check, attaching the office time zone, the booking rules, and the clash check. Move that shared logic into one function in a new module, and keep the behavior exactly as it is: the same status codes, the same messages, and the same order of checks. Don't change any tests.
```

#### Step 10: Read the plan for behavior changes

Copilot shows the plan in a **Review Plan** card. Select **Open Full Plan** to read all of it. A refactor changes structure, never behavior, so look for anything that would change what a client sees, such as a different error message, a different status code, or checks in a new order. If you find one, add a comment to the plan, or type it in the card's feedback box, and select **Submit Feedback**. Copilot revises the plan. This is the cheapest moment to catch a problem.

#### Step 11: Implement it

When the plan is right, select **Implement Plan**, and Copilot makes the change. Allow `uv run pytest` when it asks, and watch whether it runs the tests before it finishes.

#### Step 12: Review the result

Open the changed-files summary above the chat input and read the diff, then run the tests yourself:

```
uv run pytest
```

Every test should pass without having been touched. If Copilot changed a test, discard that file's changes in the Source Control view and ask Copilot why it needed to. Compare the result with our version, [Demo 4's slots.py](../04-team-feature/roombook/slots.py).

## What You Saw

- A debugging session goes better in the order a careful engineer would follow: reproduce with a failing test, find the root cause with evidence, then fix it.
- Asking what else uses the faulty code turns a symptom fix into a root-cause fix, and the extra tests prove it.
- A fix whose tests pass can still be wrong. Read the tests in a diff before the code, and check what they leave out.
- Writing a lesson into `CLAUDE.md` makes it part of every future session.
- A refactor starts with a plan you read for behavior changes, and finishes with the same tests passing, unchanged.
