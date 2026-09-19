"""Weekly recurring bookings, made and cancelled as a set.

Each occurrence is an ordinary booking that shares a series_id with the others, so the schedules,
moves, and cancellations that work for one booking work for an occurrence too.
"""

import sqlite3
import uuid
from datetime import datetime, timedelta

from roombook import db, policies
from roombook.models import SeriesRequest
from roombook.offices import OFFICES
from roombook.policies import PolicyError
from roombook.slots import SlotTaken, check_slot
from roombook.timeutils import from_db, localize, to_db, to_local_text


class SeriesRejected(Exception):
    """At least one occurrence can't be booked, so none of them were."""

    def __init__(self, failures: list[dict[str, str]]):
        super().__init__(f"{len(failures)} occurrence(s) can't be booked")
        self.failures = failures


def create(
    conn: sqlite3.Connection, room: sqlite3.Row, req: SeriesRequest, *, now: datetime
) -> tuple[str, list[int]]:
    """Book every occurrence, or none of them. Returns the series id and the new booking ids."""
    tz = OFFICES[room["office"]].tz
    slots, failures = [], []
    for week in range(req.weeks):
        # Adding whole weeks to the local wall-clock time, never to a UTC time, keeps each
        # occurrence at the same local time when the clocks change in between.
        start = req.start + timedelta(weeks=week)
        end = req.end + timedelta(weeks=week)
        try:
            slots.append(check_slot(conn, room, start, end, now=now))
        except (PolicyError, SlotTaken) as exc:
            failures.append({"start": to_local_text(localize(start, tz), tz), "reason": str(exc)})
    if failures:
        raise SeriesRejected(failures)

    series_id = uuid.uuid4().hex
    status = policies.initial_status(bool(room["requires_approval"]))
    booking_ids = [
        db.insert_booking(
            conn, room["id"], req.title, req.booked_by, to_db(start), to_db(end), status, series_id
        )
        for start, end in slots
    ]
    conn.commit()
    return series_id, booking_ids


def cancel(conn: sqlite3.Connection, series_id: str, *, now: datetime) -> None:
    """Cancel the occurrences that haven't started yet. Raises LookupError for an unknown series."""
    occurrences = db.series_bookings(conn, series_id)
    if not occurrences:
        raise LookupError(series_id)
    for booking in occurrences:
        # An occurrence that has already started stays as it was, like any booking in the past.
        if from_db(booking["start_utc"]) > now:
            db.set_status(conn, booking["id"], "cancelled")
    conn.commit()
