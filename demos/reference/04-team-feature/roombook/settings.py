"""Settings, read from the environment when the app starts."""

import os
from pathlib import Path

# Each copy of the app keeps its database next to the code, so two checkouts never share data.
DB_PATH = Path(
    os.environ.get("ROOMBOOK_DB", Path(__file__).resolve().parent.parent / "data" / "roombook.db")
)

# The sample bookings fall in late October and early November 2026. The clock is pinned to the
# start of that fortnight so the "no bookings in the past" rule doesn't reject them once the real
# date moves on. Set ROOMBOOK_NOW to another ISO time to move it, or to "system" for the real clock.
NOW = os.environ.get("ROOMBOOK_NOW", "2026-10-26T08:00:00+00:00")
