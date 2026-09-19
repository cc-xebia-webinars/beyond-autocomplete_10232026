"""The day view each office shows on the screen in its lobby."""

import sqlite3
from datetime import date

from roombook import db
from roombook.models import Schedule, ScheduleEntry
from roombook.offices import Office
from roombook.timeutils import day_bounds, from_db, to_db, to_local_text


def build(conn: sqlite3.Connection, office: Office, day: date) -> Schedule:
    start, end = day_bounds(day, office.tz)
    rows = db.office_bookings(conn, office.code, to_db(start), to_db(end))
    return Schedule(
        office=office.code,
        date=day,
        bookings=[
            ScheduleEntry(
                booking_id=row["id"],
                room=row["room_name"],
                title=row["title"],
                start=to_local_text(from_db(row["start_utc"]), office.tz),
                end=to_local_text(from_db(row["end_utc"]), office.tz),
                status=row["status"],
            )
            for row in rows
        ],
    )
