def test_lists_every_room(client):
    response = client.get("/rooms")

    assert response.status_code == 200
    assert len(response.json()) == 11


def test_filters_rooms_by_office(client):
    rooms = client.get("/rooms", params={"office": "NYC"}).json()

    assert {room["office"] for room in rooms} == {"NYC"}
    assert [room["name"] for room in rooms][:2] == ["Hudson", "Chelsea"]


def test_returns_equipment_as_a_list(client):
    room = client.get("/rooms/1").json()

    assert room["equipment"] == ["screen", "video", "whiteboard"]


def test_unknown_room_is_not_found(client):
    assert client.get("/rooms/999").status_code == 404


def available(client, **params):
    response = client.get("/rooms/available", params=params)
    names = [room["name"] for room in response.json()] if response.status_code == 200 else []
    return response.status_code, names


def test_available_rooms_filter_by_capacity_and_equipment(client):
    status, names = available(
        client,
        office="NYC",
        start="2026-10-27T14:00",
        end="2026-10-27T15:00",
        min_capacity=6,
        equipment="whiteboard",
    )

    assert status == 200
    assert names == ["Chelsea", "Midtown"]


def test_available_rooms_need_every_requested_item(client):
    _, names = available(
        client,
        office="AMS",
        start="2026-10-27T14:00",
        end="2026-10-27T15:00",
        equipment=["screen", "video"],
    )

    assert names == ["Herengracht", "Amstel Boardroom"]


def test_a_room_booked_during_the_window_is_not_available(client):
    # Hudson has the standup from 09:00 to 10:00 on 26 October.
    _, names = available(
        client, office="NYC", start="2026-10-26T09:00", end="2026-10-26T10:00", min_capacity=10
    )

    assert names == ["Midtown", "Liberty Boardroom"]


def test_a_room_is_available_from_the_minute_a_booking_ends(client):
    _, names = available(
        client, office="NYC", start="2026-10-26T10:00", end="2026-10-26T11:00", min_capacity=10
    )

    assert names == ["Hudson", "Midtown", "Liberty Boardroom"]


def test_available_rooms_reject_a_backwards_window(client):
    status, _ = available(client, office="NYC", start="2026-10-27T15:00", end="2026-10-27T14:00")

    assert status == 400
