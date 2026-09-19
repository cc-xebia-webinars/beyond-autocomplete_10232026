from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest

from roombook.policies import PolicyError, check_booking, initial_status

AMS = ZoneInfo("Europe/Amsterdam")

# Monday 26 October 2026, 08:00 UTC, which is 09:00 in Amsterdam.
NOW = datetime(2026, 10, 26, 8, 0, tzinfo=UTC)


def at(text: str) -> datetime:
    return datetime.fromisoformat(text).replace(tzinfo=AMS)


@pytest.mark.parametrize(
    ("start", "end"),
    [
        ("2026-10-27T10:00", "2026-10-27T11:00"),
        ("2026-10-27T10:00", "2026-10-27T10:15"),  # the shortest booking, one slot
        ("2026-10-27T09:00", "2026-10-27T13:00"),  # exactly four hours
        ("2026-10-27T07:00", "2026-10-27T08:00"),  # from the minute the office opens
        ("2026-10-27T21:00", "2026-10-27T22:00"),  # up to the minute it closes
        ("2027-01-24T09:00", "2027-01-24T10:00"),  # exactly 90 days ahead
    ],
)
def test_accepts_bookings_inside_the_rules(start, end):
    check_booking(at(start), at(end), now=NOW)


@pytest.mark.parametrize(
    ("start", "end", "message"),
    [
        ("2026-10-27T11:00", "2026-10-27T10:00", "end after it starts"),
        ("2026-10-27T10:00", "2026-10-27T10:00", "end after it starts"),
        ("2026-10-27T10:10", "2026-10-27T11:00", "quarter hour"),
        ("2026-10-27T10:00", "2026-10-27T10:50", "quarter hour"),
        ("2026-10-27T10:00:30", "2026-10-27T11:00", "quarter hour"),
        ("2026-10-27T09:00", "2026-10-27T13:15", "at most 4 hours"),
        ("2026-10-27T21:00", "2026-10-28T00:00", "same day"),
        ("2026-10-27T06:45", "2026-10-27T07:30", "between 07:00 and 22:00"),
        ("2026-10-27T21:00", "2026-10-27T22:15", "between 07:00 and 22:00"),
        ("2026-10-26T08:45", "2026-10-26T09:15", "already started"),
        ("2026-10-26T09:00", "2026-10-26T10:00", "already started"),
        ("2027-01-24T09:15", "2027-01-24T10:00", "up to 90 days ahead"),
    ],
)
def test_rejects_bookings_that_break_a_rule(start, end, message):
    with pytest.raises(PolicyError, match=message):
        check_booking(at(start), at(end), now=NOW)


def test_a_booking_that_crosses_midnight_is_reported_as_two_days_not_late():
    # The same-day rule is checked before opening hours, so this gets the clearer message.
    with pytest.raises(PolicyError) as excinfo:
        check_booking(at("2026-10-27T21:00"), at("2026-10-28T00:00"), now=NOW)

    assert str(excinfo.value) == "A booking has to start and end on the same day."


def test_rooms_that_need_approval_start_as_pending():
    assert initial_status(requires_approval=True) == "pending"


def test_other_rooms_are_confirmed_straight_away():
    assert initial_status(requires_approval=False) == "confirmed"
