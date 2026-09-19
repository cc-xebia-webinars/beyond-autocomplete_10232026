"""Offices and the daily schedule for each one."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from roombook import schedule
from roombook.deps import Conn
from roombook.models import OfficeInfo, Schedule
from roombook.offices import OFFICES

router = APIRouter(prefix="/offices", tags=["offices"])


@router.get("", response_model=list[OfficeInfo])
def list_offices() -> list[OfficeInfo]:
    return [
        OfficeInfo(code=office.code, name=office.name, time_zone=office.tz.key)
        for office in OFFICES.values()
    ]


@router.get("/{code}/schedule", response_model=Schedule)
def office_schedule(code: str, day: Annotated[date, Query(alias="date")], conn: Conn) -> Schedule:
    """Every active booking in the office on one local day, for the lobby screen."""
    office = OFFICES.get(code.upper())
    if office is None:
        raise HTTPException(404, f"There's no office with the code {code}.")
    return schedule.build(conn, office, day)
