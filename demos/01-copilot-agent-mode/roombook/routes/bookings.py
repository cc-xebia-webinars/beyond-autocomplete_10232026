"""Creating, moving, and cancelling bookings."""

from fastapi import APIRouter, HTTPException, Response

from roombook import availability, db, policies
from roombook.deps import Conn, Now
from roombook.models import Booking, BookingMove, BookingRequest
from roombook.offices import OFFICES
from roombook.policies import PolicyError
from roombook.timeutils import localize, to_db

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=Booking, status_code=201)
def create_booking(req: BookingRequest, conn: Conn, now: Now) -> Booking:
    room = db.get_room(conn, req.room_id)
    if room is None:
        raise HTTPException(404, "Room not found.")
    tz = OFFICES[room["office"]].tz
    if req.start.tzinfo is not None or req.end.tzinfo is not None:
        raise HTTPException(400, "Send times in the office's local time, without an offset.")
    start = localize(req.start, tz)
    end = localize(req.end, tz)
    try:
        policies.check_booking(start, end, now=now)
    except PolicyError as exc:
        raise HTTPException(400, str(exc)) from exc
    clashes = availability.conflicts(conn, room["id"], start, end)
    if clashes:
        raise HTTPException(409, f"{room['name']} is already booked then: {clashes[0]['title']}.")
    status = policies.initial_status(bool(room["requires_approval"]))
    booking_id = db.insert_booking(
        conn, room["id"], req.title, req.booked_by, to_db(start), to_db(end), status
    )
    conn.commit()
    return Booking.from_row(db.get_booking(conn, booking_id), tz)


@router.get("/{booking_id}", response_model=Booking)
def get_booking(booking_id: int, conn: Conn) -> Booking:
    booking = db.get_booking(conn, booking_id)
    if booking is None:
        raise HTTPException(404, "Booking not found.")
    room = db.get_room(conn, booking["room_id"])
    return Booking.from_row(booking, OFFICES[room["office"]].tz)


@router.patch("/{booking_id}", response_model=Booking)
def move_booking(booking_id: int, req: BookingMove, conn: Conn, now: Now) -> Booking:
    booking = db.get_booking(conn, booking_id)
    if booking is None:
        raise HTTPException(404, "Booking not found.")
    if booking["status"] == "cancelled":
        raise HTTPException(409, "That booking was cancelled, so it can't be moved.")
    room = db.get_room(conn, booking["room_id"])
    tz = OFFICES[room["office"]].tz
    if req.start.tzinfo is not None or req.end.tzinfo is not None:
        raise HTTPException(400, "Send times in the office's local time, without an offset.")
    start = localize(req.start, tz)
    end = localize(req.end, tz)
    try:
        policies.check_booking(start, end, now=now)
    except PolicyError as exc:
        raise HTTPException(400, str(exc)) from exc
    clashes = availability.conflicts(conn, room["id"], start, end, ignore_booking_id=booking_id)
    if clashes:
        raise HTTPException(409, f"{room['name']} is already booked then: {clashes[0]['title']}.")
    # The manager approved the old time, not the new one, so a moved boardroom booking is pending.
    status = policies.initial_status(bool(room["requires_approval"]))
    db.update_booking_times(conn, booking_id, to_db(start), to_db(end), status)
    conn.commit()
    return Booking.from_row(db.get_booking(conn, booking_id), tz)


@router.delete("/{booking_id}", status_code=204)
def cancel_booking(booking_id: int, conn: Conn) -> Response:
    # Cancelled bookings stay in the table, so the office managers can see what was given up.
    if db.get_booking(conn, booking_id) is None:
        raise HTTPException(404, "Booking not found.")
    db.set_status(conn, booking_id, "cancelled")
    conn.commit()
    return Response(status_code=204)
