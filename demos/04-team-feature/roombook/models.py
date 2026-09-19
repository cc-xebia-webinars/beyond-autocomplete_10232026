"""Request and response shapes for the API."""

import sqlite3
from datetime import date, datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

from roombook.timeutils import from_db, to_local_text


class Room(BaseModel):
    id: int
    office: str
    name: str
    capacity: int
    equipment: list[str]
    requires_approval: bool

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Room:
        return cls(
            id=row["id"],
            office=row["office"],
            name=row["name"],
            capacity=row["capacity"],
            # Stored as comma-separated text, such as "screen,whiteboard". Empty means none.
            equipment=[item for item in row["equipment"].split(",") if item],
            requires_approval=bool(row["requires_approval"]),
        )


class BookingRequest(BaseModel):
    room_id: int
    title: str = Field(min_length=1, max_length=100)
    booked_by: str = Field(min_length=1, max_length=100)
    start: datetime = Field(description="Local office time without an offset: 2026-10-27T09:00")
    end: datetime = Field(description="Local office time without an offset: 2026-10-27T10:00")


class BookingMove(BaseModel):
    start: datetime = Field(description="New local start time, without an offset")
    end: datetime = Field(description="New local end time, without an offset")


class Booking(BaseModel):
    id: int
    room_id: int
    title: str
    booked_by: str
    start: str = Field(description="Local office time")
    end: str = Field(description="Local office time")
    status: str

    @classmethod
    def from_row(cls, row: sqlite3.Row, tz: ZoneInfo) -> Booking:
        return cls(
            id=row["id"],
            room_id=row["room_id"],
            title=row["title"],
            booked_by=row["booked_by"],
            start=to_local_text(from_db(row["start_utc"]), tz),
            end=to_local_text(from_db(row["end_utc"]), tz),
            status=row["status"],
        )


class OfficeInfo(BaseModel):
    code: str
    name: str
    time_zone: str


class ScheduleEntry(BaseModel):
    booking_id: int
    room: str
    title: str
    start: str = Field(description="Local office time")
    end: str = Field(description="Local office time")
    status: str


class Schedule(BaseModel):
    office: str
    date: date
    bookings: list[ScheduleEntry]
