"""Time zone helpers.

Bookings are stored in UTC and shown in the office's local time. People always book in local
time, because that's the time on the meeting invite.
"""

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

# One fixed format, always in UTC, so SQLite can compare stored times as plain strings.
DB_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def localize(value: datetime, tz: ZoneInfo) -> datetime:
    """Attach an office's time zone to a wall-clock time from a request."""
    return value.replace(tzinfo=tz)


def to_db(value: datetime) -> str:
    return value.astimezone(UTC).strftime(DB_FORMAT)


def from_db(value: str) -> datetime:
    return datetime.strptime(value, DB_FORMAT).replace(tzinfo=UTC)


def to_local_text(value: datetime, tz: ZoneInfo) -> str:
    """Format a time the way the API returns it: local wall-clock time, to the minute."""
    return value.astimezone(tz).strftime("%Y-%m-%dT%H:%M")


def day_bounds(day: date, tz: ZoneInfo) -> tuple[datetime, datetime]:
    """Return the start and end of a calendar day in an office, for querying bookings."""
    start = datetime.combine(day, time.min, tzinfo=UTC).astimezone(tz)
    return start, start + timedelta(days=1)
