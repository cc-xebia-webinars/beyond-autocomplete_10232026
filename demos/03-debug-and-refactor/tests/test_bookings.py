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


def test_rejects_times_sent_with_an_offset(client):
    response = book(client, 7, "2026-10-27T10:00+02:00", "2026-10-27T11:00+02:00")

    assert response.status_code == 400


def test_a_booking_can_shrink_within_its_own_time(client):
    booking_id = book(client, 7, "2026-10-27T10:00", "2026-10-27T11:00").json()["id"]

    response = client.patch(
        f"/bookings/{booking_id}", json={"start": "2026-10-27T10:00", "end": "2026-10-27T10:30"}
    )

    assert response.status_code == 200


def test_rejects_a_move_onto_another_booking(client):
    booking_id = book(client, 6, "2026-10-26T11:00", "2026-10-26T12:00").json()["id"]

    response = client.patch(
        f"/bookings/{booking_id}", json={"start": "2026-10-26T09:30", "end": "2026-10-26T10:30"}
    )

    assert response.status_code == 409


def test_a_moved_boardroom_booking_needs_approval_again(client):
    # Booking 12 is the confirmed board prep in the Liberty Boardroom on 28 October.
    response = client.patch(
        "/bookings/12", json={"start": "2026-10-28T13:00", "end": "2026-10-28T15:00"}
    )

    assert response.json()["status"] == "pending"


def test_a_cancelled_booking_cannot_be_moved(client):
    # Booking 19 is the lunch and learn on 30 October, which was cancelled.
    response = client.patch(
        "/bookings/19", json={"start": "2026-10-30T13:00", "end": "2026-10-30T14:00"}
    )

    assert response.status_code == 409


def test_rejects_a_move_outside_opening_hours(client):
    booking_id = book(client, 7, "2026-10-27T10:00", "2026-10-27T11:00").json()["id"]

    response = client.patch(
        f"/bookings/{booking_id}", json={"start": "2026-10-27T21:30", "end": "2026-10-27T22:30"}
    )

    assert response.status_code == 400


def test_rejects_a_booking_for_an_unknown_room(client):
    assert book(client, 999, "2026-10-27T10:00", "2026-10-27T11:00").status_code == 404
