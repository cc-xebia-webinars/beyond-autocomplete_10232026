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
