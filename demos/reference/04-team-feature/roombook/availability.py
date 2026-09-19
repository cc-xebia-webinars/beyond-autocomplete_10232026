"""Whether a room is free, and what's in the way when it isn't."""

import sqlite3
from datetime import datetime

from roombook import db
from roombook.timeutils import to_db


def conflicts(
    conn: sqlite3.Connection,
    room_id: int,
    start: datetime,
    end: datetime,
    ignore_booking_id: int | None = None,
) -> list[sqlite3.Row]:
    """Return the room's active bookings that overlap a window.

    Bookings are half-open intervals, so one that ends at 10:00 leaves the room free for one
    that starts at 10:00. Moving a booking passes its own id as ignore_booking_id, so that it
    doesn't clash with itself.
    """
    rows = conn.execute(
        "SELECT * FROM bookings WHERE room_id = ? AND status != 'cancelled'"
        " AND start_utc < ? AND end_utc > ? ORDER BY start_utc",
        (room_id, to_db(end), to_db(start)),
    ).fetchall()
    return [row for row in rows if row["id"] != ignore_booking_id]


def has_equipment(room: sqlite3.Row, required: list[str]) -> bool:
    """True if the room has every item in required. Equipment is stored comma-separated."""
    return set(required) <= set(room["equipment"].split(","))


def free_rooms(
    conn: sqlite3.Connection,
    office: str,
    start: datetime,
    end: datetime,
    min_capacity: int = 1,
    equipment: list[str] | None = None,
) -> list[sqlite3.Row]:
    """Rooms in an office that are big enough, have the equipment, and are free for the window."""
    return [
        room
        for room in db.list_rooms(conn, office)
        if room["capacity"] >= min_capacity
        and has_equipment(room, equipment or [])
        and not conflicts(conn, room["id"], start, end)
    ]
