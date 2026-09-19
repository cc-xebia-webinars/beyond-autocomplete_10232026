from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from roombook.timeutils import day_bounds

NYC = ZoneInfo("America/New_York")
AMS = ZoneInfo("Europe/Amsterdam")


def test_a_new_york_day_runs_from_local_midnight_to_local_midnight():
    start, end = day_bounds(date(2026, 10, 27), NYC)

    assert start == datetime(2026, 10, 27, 4, 0, tzinfo=UTC)
    assert end == datetime(2026, 10, 28, 4, 0, tzinfo=UTC)


@pytest.mark.parametrize(
    ("day", "tz", "hours"),
    [
        (date(2026, 10, 27), NYC, 24),
        (date(2026, 11, 1), NYC, 25),  # New York's clocks go back an hour
        (date(2026, 10, 25), AMS, 25),  # Amsterdam's clocks go back an hour
        (date(2027, 3, 14), NYC, 23),  # New York's clocks go forward an hour
    ],
)
def test_a_day_is_as_long_as_the_office_clock_says(day, tz, hours):
    start, end = day_bounds(day, tz)

    # Compare in UTC, because subtracting two times in the same zone ignores the clock change.
    assert end.astimezone(UTC) - start.astimezone(UTC) == timedelta(hours=hours)
