"""Booking rules.

Every rule here came from the office managers, so change one only when they ask for it.
"""

from datetime import datetime, time, timedelta

SLOT_MINUTES = 15
LONGEST = timedelta(hours=4)
OPENS = time(7, 0)
CLOSES = time(22, 0)
HORIZON = timedelta(days=90)


class PolicyError(ValueError):
    """A booking breaks a rule. The message goes back to the person booking, so keep it plain."""


def check_booking(start: datetime, end: datetime, *, now: datetime) -> None:
    """Raise PolicyError if a booking breaks a rule.

    start and end are local office times with the office's time zone attached. now is passed in
    rather than read from the clock so that tests can pin it.
    """
    if end <= start:
        raise PolicyError("A booking has to end after it starts.")
    for moment in (start, end):
        if moment.minute % SLOT_MINUTES or moment.second or moment.microsecond:
            raise PolicyError("Bookings start and end on the quarter hour.")
    if end - start > LONGEST:
        raise PolicyError("Bookings can be at most 4 hours long.")
    if start.date() != end.date():
        raise PolicyError("A booking has to start and end on the same day.")
    if start.time() < OPENS or end.time() > CLOSES:
        raise PolicyError("Rooms can be booked between 07:00 and 22:00 office time.")
    if start <= now:
        raise PolicyError("That time has already started.")
    if start - now > HORIZON:
        raise PolicyError("Bookings can be made up to 90 days ahead.")


def initial_status(requires_approval: bool) -> str:
    # The boardrooms hold a booking as pending until an office manager confirms it.
    return "pending" if requires_approval else "confirmed"
