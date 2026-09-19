"""Sample data: eleven rooms and two weeks of bookings in both offices.

The app loads this the first time it starts with an empty database. To throw the database away
and build it again, run:

    uv run python -m roombook.seed --reset

The bookings span Amsterdam's clock change on 25 October and New York's on 1 November 2026, so
the gap between the offices is five hours for the first week and six hours after that.
"""

import argparse
import sqlite3
from datetime import datetime

from roombook import db, settings
from roombook.offices import OFFICES
from roombook.timeutils import localize, to_db

# fmt: off
ROOMS = [
    # id, office, name, capacity, equipment, requires approval
    (1, "AMS", "Herengracht", 12, "screen,video,whiteboard", False),
    (2, "AMS", "Keizersgracht", 8, "screen,whiteboard", False),
    (3, "AMS", "Prinsengracht", 4, "screen", False),
    (4, "AMS", "Singel", 2, "", False),
    (5, "AMS", "Amstel Boardroom", 16, "screen,video", True),
    (6, "NYC", "Hudson", 10, "screen,video", False),
    (7, "NYC", "Chelsea", 6, "screen,whiteboard", False),
    (8, "NYC", "Tribeca", 4, "screen", False),
    (9, "NYC", "SoHo", 2, "", False),
    (10, "NYC", "Midtown", 14, "screen,video,whiteboard", False),
    (11, "NYC", "Liberty Boardroom", 20, "screen,video", True),
]

BOOKINGS = [
    # room id, title, booked by, local start, local end, status
    (1, "Sprint planning", "Sanne de Vries", "2026-10-26 09:30", "2026-10-26 11:00", "confirmed"),
    (2, "Design review", "Pieter Bakker", "2026-10-26 13:00", "2026-10-26 14:00", "confirmed"),
    (6, "Standup and planning", "Maria Lopez", "2026-10-26 09:00", "2026-10-26 10:00", "confirmed"),
    (7, "Sales pipeline review", "James Carter", "2026-10-26 14:00", "2026-10-26 15:00", "confirmed"),
    (3, "1:1 Sanne and Daan", "Daan Jansen", "2026-10-27 08:30", "2026-10-27 09:00", "confirmed"),
    (1, "Architecture guild", "Lotte Visser", "2026-10-27 10:00", "2026-10-27 12:00", "confirmed"),
    (2, "Customer call: Northwind", "Pieter Bakker", "2026-10-27 15:00", "2026-10-27 16:00", "confirmed"),
    (8, "1:1 Priya and Sam", "Priya Shah", "2026-10-27 11:00", "2026-10-27 11:30", "confirmed"),
    (10, "Launch rehearsal", "Ava Thompson", "2026-10-27 20:00", "2026-10-27 21:30", "confirmed"),
    (5, "Quarterly board meeting", "Femke Mulder", "2026-10-28 09:00", "2026-10-28 13:00", "confirmed"),
    (4, "Interview: backend engineer", "Lotte Visser", "2026-10-28 14:00", "2026-10-28 15:00", "confirmed"),
    (11, "Board prep", "Robert Kim", "2026-10-28 09:00", "2026-10-28 11:00", "confirmed"),
    (7, "Interview: product designer", "James Carter", "2026-10-28 13:00", "2026-10-28 14:00", "confirmed"),
    (1, "All-hands watch party", "Sanne de Vries", "2026-10-29 17:00", "2026-10-29 18:00", "confirmed"),
    (9, "Focus time", "Sam Rivera", "2026-10-29 10:00", "2026-10-29 12:00", "confirmed"),
    (6, "Customer webinar", "Maria Lopez", "2026-10-29 19:00", "2026-10-29 20:30", "confirmed"),
    (3, "Pairing session", "Daan Jansen", "2026-10-30 10:00", "2026-10-30 12:00", "confirmed"),
    (10, "Partner workshop", "Ava Thompson", "2026-10-30 09:00", "2026-10-30 12:00", "confirmed"),
    (8, "Lunch and learn", "Priya Shah", "2026-10-30 12:00", "2026-10-30 13:00", "cancelled"),
    (2, "Retro", "Sanne de Vries", "2026-11-02 15:00", "2026-11-02 16:00", "confirmed"),
    (6, "Weekly standup", "Maria Lopez", "2026-11-02 09:00", "2026-11-02 09:30", "confirmed"),
    (5, "Investor update", "Femke Mulder", "2026-11-03 10:00", "2026-11-03 11:30", "pending"),
    (10, "Town hall dry run", "Ava Thompson", "2026-11-03 19:00", "2026-11-03 20:30", "confirmed"),
    (11, "Quarterly business review", "Robert Kim", "2026-11-04 13:00", "2026-11-04 16:00", "pending"),
    (1, "Hackathon kickoff", "Lotte Visser", "2026-11-05 09:00", "2026-11-05 10:00", "confirmed"),
    (7, "Customer call: Contoso", "James Carter", "2026-11-05 16:00", "2026-11-05 17:00", "confirmed"),
    (6, "Evening meetup: Python NYC", "Sam Rivera", "2026-11-05 18:00", "2026-11-05 19:30", "confirmed"),
]
# fmt: on


def load(conn: sqlite3.Connection) -> None:
    conn.executemany(
        "INSERT INTO rooms (id, office, name, capacity, equipment, requires_approval)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        ROOMS,
    )
    office_of = {room_id: office for room_id, office, *_ in ROOMS}
    for room_id, title, booked_by, start, end, status in BOOKINGS:
        # The sample data is written in local time, the way people book, and stored in UTC.
        tz = OFFICES[office_of[room_id]].tz
        db.insert_booking(
            conn,
            room_id,
            title,
            booked_by,
            to_db(localize(datetime.fromisoformat(start), tz)),
            to_db(localize(datetime.fromisoformat(end), tz)),
            status,
        )
    conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Roombook sample database.")
    parser.add_argument("--reset", action="store_true", help="delete the database and rebuild it")
    args = parser.parse_args()

    path = settings.DB_PATH
    if args.reset:
        path.unlink(missing_ok=True)
    conn = db.connect(path)
    try:
        db.init_schema(conn)
        if db.is_empty(conn):
            load(conn)
        rooms = conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
        bookings = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    finally:
        conn.close()
    print(f"{path}: {rooms} rooms, {bookings} bookings")


if __name__ == "__main__":
    main()
