"""The Roombook API.

Run it from this folder with `uv run uvicorn roombook.main:app --reload`, then open
http://127.0.0.1:8000/docs to try the endpoints.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from roombook import db, seed, settings
from roombook.routes import bookings, offices, rooms


def create_app(db_path: Path | None = None) -> FastAPI:
    """Build the app. Tests pass a database path of their own, so they never touch the real one."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # A fresh checkout has no database yet, so the first start builds and seeds one.
        conn = db.connect(app.state.db_path)
        try:
            db.init_schema(conn)
            if db.is_empty(conn):
                seed.load(conn)
        finally:
            conn.close()
        yield

    app = FastAPI(
        title="Roombook",
        summary="Meeting-room bookings for the Amsterdam and New York offices.",
        lifespan=lifespan,
    )
    app.state.db_path = db_path or settings.DB_PATH
    for module in (rooms, bookings, offices):
        app.include_router(module.router)
    return app


app = create_app()
