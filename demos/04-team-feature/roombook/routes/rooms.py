"""Rooms and their bookings."""

from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from roombook import availability, db
from roombook.deps import Conn
from roombook.models import Booking, Room
from roombook.offices import OFFICES
from roombook.timeutils import day_bounds, localize, to_db

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=list[Room])
def list_rooms(conn: Conn, office: str | None = None) -> list[Room]:
    if office is not None and office not in OFFICES:
        raise HTTPException(404, f"There's no office with the code {office}.")
    return [Room.from_row(row) for row in db.list_rooms(conn, office)]


# This route has to come before /{room_id}. FastAPI matches routes in order, and "available"
# would otherwise be read as a room id and rejected because it isn't a number.
@router.get("/available", response_model=list[Room])
def available_rooms(
    office: str,
    start: datetime,
    end: datetime,
    conn: Conn,
    min_capacity: int = 1,
    equipment: Annotated[list[str] | None, Query()] = None,
) -> list[Room]:
    """Rooms that are free for the whole window. Times are local to the office, as for bookings."""
    if office not in OFFICES:
        raise HTTPException(404, f"There's no office with the code {office}.")
    if start.tzinfo is not None or end.tzinfo is not None:
        raise HTTPException(400, "Send times in the office's local time, without an offset.")
    if end <= start:
        raise HTTPException(400, "The window has to end after it starts.")
    tz = OFFICES[office].tz
    rows = availability.free_rooms(
        conn, office, localize(start, tz), localize(end, tz), min_capacity, equipment
    )
    return [Room.from_row(row) for row in rows]


@router.get("/{room_id}", response_model=Room)
def get_room(room_id: int, conn: Conn) -> Room:
    row = db.get_room(conn, room_id)
    if row is None:
        raise HTTPException(404, "Room not found.")
    return Room.from_row(row)


@router.get("/{room_id}/bookings", response_model=list[Booking])
def room_bookings(room_id: int, day: date, conn: Conn) -> list[Booking]:
    """A room's bookings on one day, in the room's local time."""
    room = db.get_room(conn, room_id)
    if room is None:
        raise HTTPException(404, "Room not found.")
    tz = OFFICES[room["office"]].tz
    start, end = day_bounds(day, tz)
    return [
        Booking.from_row(row, tz)
        for row in db.room_bookings(conn, room_id, to_db(start), to_db(end))
    ]
