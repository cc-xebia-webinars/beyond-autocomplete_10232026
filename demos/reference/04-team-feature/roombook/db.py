"""SQLite storage. Each request gets its own connection from the get_conn dependency."""

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY,
    office TEXT NOT NULL,
    name TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    equipment TEXT NOT NULL DEFAULT '',
    requires_approval INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY,
    room_id INTEGER NOT NULL REFERENCES rooms (id),
    title TEXT NOT NULL,
    booked_by TEXT NOT NULL,
    start_utc TEXT NOT NULL,
    end_utc TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'confirmed',
    series_id TEXT
);
"""


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    # FastAPI may open the connection on one worker thread and use it on another.
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)


def is_empty(conn: sqlite3.Connection) -> bool:
    return conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0] == 0


def list_rooms(conn: sqlite3.Connection, office: str | None = None) -> list[sqlite3.Row]:
    if office is None:
        return conn.execute("SELECT * FROM rooms ORDER BY id").fetchall()
    return conn.execute("SELECT * FROM rooms WHERE office = ? ORDER BY id", (office,)).fetchall()


def get_room(conn: sqlite3.Connection, room_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM rooms WHERE id = ?", (room_id,)).fetchone()


def get_booking(conn: sqlite3.Connection, booking_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()


def insert_booking(
    conn: sqlite3.Connection,
    room_id: int,
    title: str,
    booked_by: str,
    start_utc: str,
    end_utc: str,
    status: str,
    series_id: str | None = None,
) -> int:
    cur = conn.execute(
        "INSERT INTO bookings (room_id, title, booked_by, start_utc, end_utc, status, series_id)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (room_id, title, booked_by, start_utc, end_utc, status, series_id),
    )
    return cur.lastrowid


def update_booking_times(
    conn: sqlite3.Connection, booking_id: int, start_utc: str, end_utc: str, status: str
) -> None:
    conn.execute(
        "UPDATE bookings SET start_utc = ?, end_utc = ?, status = ? WHERE id = ?",
        (start_utc, end_utc, status, booking_id),
    )


def set_status(conn: sqlite3.Connection, booking_id: int, status: str) -> None:
    conn.execute("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))


def room_bookings(
    conn: sqlite3.Connection, room_id: int, start_utc: str, end_utc: str
) -> list[sqlite3.Row]:
    """Active bookings for one room that start inside a window."""
    return conn.execute(
        "SELECT * FROM bookings WHERE room_id = ? AND status != 'cancelled'"
        " AND start_utc >= ? AND start_utc < ? ORDER BY start_utc",
        (room_id, start_utc, end_utc),
    ).fetchall()


def office_bookings(
    conn: sqlite3.Connection, office: str, start_utc: str, end_utc: str
) -> list[sqlite3.Row]:
    """Active bookings for every room in an office that start inside a window."""
    return conn.execute(
        "SELECT b.*, r.name AS room_name FROM bookings b JOIN rooms r ON r.id = b.room_id"
        " WHERE r.office = ? AND b.status != 'cancelled' AND b.start_utc >= ? AND b.start_utc < ?"
        " ORDER BY b.start_utc, r.name",
        (office, start_utc, end_utc),
    ).fetchall()


def series_bookings(conn: sqlite3.Connection, series_id: str) -> list[sqlite3.Row]:
    """Every occurrence in a series, cancelled ones included, in date order."""
    return conn.execute(
        "SELECT * FROM bookings WHERE series_id = ? ORDER BY start_utc", (series_id,)
    ).fetchall()
