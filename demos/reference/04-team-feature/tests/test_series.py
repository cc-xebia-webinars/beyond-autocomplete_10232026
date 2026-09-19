"""Weekly recurring bookings, one test per acceptance criterion in docs/specs/recurring-bookings.md."""

from datetime import UTC, datetime

from roombook.deps import get_now


def book_series(client, room_id, start, end, weeks, title="Weekly planning"):
    return client.post(
        "/bookings/series",
        json={
            "room_id": room_id,
            "title": title,
            "booked_by": "Test User",
            "start": start,
            "end": end,
            "weeks": weeks,
        },
    )


def titles_on(client, office, day):
    schedule = client.get(f"/offices/{office}/schedule", params={"date": day}).json()
    return [entry["title"] for entry in schedule["bookings"]]


def test_each_occurrence_keeps_its_local_time_across_the_clock_change(client):
    response = book_series(client, 10, "2026-10-27T10:00", "2026-10-27T11:00", weeks=4)

    assert response.status_code == 201
    occurrences = [(b["start"], b["end"]) for b in response.json()["bookings"]]
    assert occurrences == [
        ("2026-10-27T10:00", "2026-10-27T11:00"),
        ("2026-11-03T10:00", "2026-11-03T11:00"),
        ("2026-11-10T10:00", "2026-11-10T11:00"),
        ("2026-11-17T10:00", "2026-11-17T11:00"),
    ]


def test_a_clash_in_one_week_rejects_the_whole_series(client):
    response = book_series(client, 10, "2026-10-27T19:00", "2026-10-27T20:00", weeks=3)

    assert response.status_code == 409
    assert response.json()["detail"] == [
        {
            "start": "2026-11-03T19:00",
            "reason": "Midtown is already booked then: Town hall dry run.",
        }
    ]
    # Nothing was saved, not even the weeks that were free.
    assert "Weekly planning" not in titles_on(client, "NYC", "2026-10-27")


def test_occurrences_past_the_booking_horizon_are_listed(client):
    # The clock is at 26 October, so 26 January 2027 is more than 90 days ahead.
    response = book_series(client, 2, "2027-01-05T10:00", "2027-01-05T11:00", weeks=4)

    assert response.status_code == 409
    assert [failure["start"] for failure in response.json()["detail"]] == ["2027-01-26T10:00"]


def test_a_series_needs_between_two_and_twelve_weeks(client):
    for weeks in (1, 13):
        response = book_series(client, 2, "2026-11-02T10:00", "2026-11-02T11:00", weeks=weeks)

        assert response.status_code == 422


def test_cancelling_a_series_leaves_occurrences_that_have_started(client):
    created = book_series(client, 10, "2026-10-27T10:00", "2026-10-27T11:00", weeks=4).json()
    # Half an hour into the first occurrence, which started at 10:00 New York time (14:00 UTC).
    client.app.dependency_overrides[get_now] = lambda: datetime(2026, 10, 27, 14, 30, tzinfo=UTC)

    response = client.delete(f"/bookings/series/{created['series_id']}")

    assert response.status_code == 204
    statuses = [client.get(f"/bookings/{b['id']}").json()["status"] for b in created["bookings"]]
    assert statuses == ["confirmed", "cancelled", "cancelled", "cancelled"]


def test_cancelling_an_unknown_series_is_not_found(client):
    assert client.delete("/bookings/series/no-such-series").status_code == 404


def test_occurrences_are_ordinary_bookings_on_the_schedule(client):
    book_series(client, 10, "2026-10-27T10:00", "2026-10-27T11:00", weeks=2)

    assert "Weekly planning" in titles_on(client, "NYC", "2026-11-03")
