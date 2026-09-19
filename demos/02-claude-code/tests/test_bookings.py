def book(client, room_id, start, end, title="Team sync"):
    return client.post(
        "/bookings",
        json={
            "room_id": room_id,
            "title": title,
            "booked_by": "Test User",
            "start": start,
            "end": end,
        },
    )


def test_creates_a_confirmed_booking_in_local_time(client):
    response = book(client, 7, "2026-10-27T10:00", "2026-10-27T11:00")

    assert response.status_code == 201
    booking = response.json()
    assert booking["status"] == "confirmed"
    assert (booking["start"], booking["end"]) == ("2026-10-27T10:00", "2026-10-27T11:00")


def test_boardroom_bookings_wait_for_approval(client):
    response = book(client, 11, "2026-10-29T14:00", "2026-10-29T15:00")

    assert response.json()["status"] == "pending"


def test_rejects_an_overlapping_booking(client):
    # Hudson has the standup from 09:00 to 10:00 on 26 October.
    response = book(client, 6, "2026-10-26T09:30", "2026-10-26T10:30")

    assert response.status_code == 409
    assert "Standup and planning" in response.json()["detail"]


def test_allows_a_booking_that_starts_when_another_ends(client):
    response = book(client, 6, "2026-10-26T10:00", "2026-10-26T11:00")

    assert response.status_code == 201


def test_rejects_a_booking_outside_opening_hours(client):
    response = book(client, 6, "2026-10-27T06:30", "2026-10-27T07:30")

    assert response.status_code == 400


def test_moves_a_booking(client):
    booking_id = book(client, 7, "2026-10-27T10:00", "2026-10-27T11:00").json()["id"]

    response = client.patch(
        f"/bookings/{booking_id}", json={"start": "2026-10-27T10:30", "end": "2026-10-27T11:30"}
    )

    assert response.status_code == 200
    assert response.json()["start"] == "2026-10-27T10:30"


def test_cancels_a_booking(client):
    booking_id = book(client, 7, "2026-10-27T10:00", "2026-10-27T11:00").json()["id"]

    assert client.delete(f"/bookings/{booking_id}").status_code == 204
    assert client.get(f"/bookings/{booking_id}").json()["status"] == "cancelled"
