"""Rooms and their bookings."""

from datetime import date

from fastapi import APIRouter, HTTPException

from roombook import db
from roombook.deps import Conn
from roombook.models import Booking, Room
from roombook.offices import OFFICES
from roombook.timeutils import day_bounds, to_db

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=list[Room])
def list_rooms(conn: Conn, office: str | None = None) -> list[Room]:
    if office is not None and office not in OFFICES:
        raise HTTPException(404, f"There's no office with the code {office}.")
    return [Room.from_row(row) for row in db.list_rooms(conn, office)]


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
