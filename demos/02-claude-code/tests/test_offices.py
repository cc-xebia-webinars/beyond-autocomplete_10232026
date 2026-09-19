def test_lists_both_offices(client):
    offices = client.get("/offices").json()

    assert [office["code"] for office in offices] == ["AMS", "NYC"]


def test_amsterdam_schedule_lists_the_day_in_order(client):
    schedule = client.get("/offices/AMS/schedule", params={"date": "2026-10-27"}).json()

    assert [entry["title"] for entry in schedule["bookings"]] == [
        "1:1 Sanne and Daan",
        "Architecture guild",
        "Customer call: Northwind",
    ]
    assert schedule["bookings"][0]["start"] == "2026-10-27T08:30"


def test_new_york_schedule_skips_cancelled_bookings(client):
    schedule = client.get("/offices/NYC/schedule", params={"date": "2026-10-30"}).json()

    assert [entry["title"] for entry in schedule["bookings"]] == ["Partner workshop"]
