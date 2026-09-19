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


def titles(client, office, day):
    schedule = client.get(f"/offices/{office}/schedule", params={"date": day}).json()
    return [entry["title"] for entry in schedule["bookings"]]


def test_an_evening_booking_is_on_its_own_day_in_new_york(client):
    # Issue #42: the 20:00 launch rehearsal on 27 October showed up on the 28th.
    assert "Launch rehearsal" in titles(client, "NYC", "2026-10-27")
    assert "Launch rehearsal" not in titles(client, "NYC", "2026-10-28")


def test_an_evening_booking_after_the_clock_change_is_on_its_own_day(client):
    # From 1 November New York is five hours behind UTC, so 19:00 is already tomorrow in UTC.
    assert "Town hall dry run" in titles(client, "NYC", "2026-11-03")
    assert "Town hall dry run" not in titles(client, "NYC", "2026-11-04")
