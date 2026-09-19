# #42: Evening bookings missing from the New York lobby schedule

- **Reported by:** Ava Thompson, New York office
- **Severity:** Medium. People walk into rooms the lobby screen says are free.

## What happened

I checked the New York schedule for Tuesday, 27 October, to plan the setup for our launch rehearsal, and the rehearsal isn't on it. It's booked in Midtown from 8:00 to 9:30 pm, and the booking itself looks fine. When I open Wednesday's schedule (28 October), the rehearsal is at the top of the list, still showing a start of `2026-10-27T20:00`.

It isn't every evening booking. Maria's customer webinar on Thursday, 29 October, from 7:00 to 8:30 pm in Hudson is on Thursday's schedule where it belongs.

The Amsterdam team says their schedule looks right.

## Steps to reproduce

1. Start the API with the sample data.
2. Open `GET /offices/NYC/schedule?date=2026-10-27`.
3. Open `GET /offices/NYC/schedule?date=2026-10-28`.

## Expected

The launch rehearsal is on the schedule for 27 October and not on the one for 28 October.
