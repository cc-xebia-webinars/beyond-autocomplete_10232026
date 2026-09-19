# Reference: Demo 4, Finished

This folder holds a finished version of [Demo 4](../04-team-feature/README.md) to compare with what Claude builds for you. It lives here, outside the demo folder, so neither agent can find it while it's working on the demo.

| What | Where |
|------|-------|
| The shared project instructions, read by Copilot and Claude Code | `04-team-feature/AGENTS.md` |
| A `CLAUDE.md` that imports them and adds notes only Claude needs | `04-team-feature/CLAUDE.md` |
| The recurring-bookings logic | `04-team-feature/roombook/series.py` |
| The two new routes | The end of `04-team-feature/roombook/routes/bookings.py` |
| One test for each acceptance criterion in the spec | `04-team-feature/tests/test_series.py` |

The detail to look for is in `roombook/series.py`. Each occurrence is worked out by adding whole weeks to the local wall-clock time, so a Tuesday 10:00 booking is still at 10:00 after New York's clocks go back on 1 November. Adding the weeks to a UTC time instead lands every later occurrence at 09:00, and the first acceptance test catches it.

To run the finished version's tests, open a terminal in this folder's `04-team-feature` subfolder and install its dependencies:

```
uv sync
```

Then run the tests:

```
uv run pytest
```

All 62 pass: the 55 tests Demo 4 starts with, unchanged, and 7 new ones for the series.

## Review Exercise for Demo 3

`review-exercise/issue-42-agent-fix.diff` is a plausible but wrong fix for the bug in [Demo 3](../03-debug-and-refactor/README.md), the kind an agent produces when it fixes the symptom. Its tests pass. Demo 3's Step 6 asks you to review it and find what's wrong, and lists what to look for. It's here, outside the demo folder, so neither agent mistakes it for the answer while it's debugging.
