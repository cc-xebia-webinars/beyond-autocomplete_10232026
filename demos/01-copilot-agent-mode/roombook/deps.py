"""Dependencies that FastAPI passes to the route functions."""

import sqlite3
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, Request

from roombook import db, settings


def get_conn(request: Request) -> Iterator[sqlite3.Connection]:
    conn = db.connect(request.app.state.db_path)
    try:
        yield conn
    finally:
        conn.close()


def get_now() -> datetime:
    # Routes ask for the time through this dependency, so tests can override it with a fixed one.
    if settings.NOW == "system":
        return datetime.now(UTC)
    return datetime.fromisoformat(settings.NOW)


Conn = Annotated[sqlite3.Connection, Depends(get_conn)]
Now = Annotated[datetime, Depends(get_now)]
