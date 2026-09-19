# Spec: Weekly Recurring Bookings

## Goal

Teams want to book the same room at the same time every week, such as a Tuesday planning session, without making each booking by hand.

## Context

- Bookings are created in `roombook/routes/bookings.py`. Every new or moved booking goes through `check_slot` in `roombook/slots.py`, which applies the booking rules and checks for clashes.
- Times in requests are local to the room's office. Both offices change their clocks during the sample data: Amsterdam on 25 October and New York on 1 November 2026.

## What to Build

- `POST /bookings/series` takes the same fields as `POST /bookings`, plus `weeks`: the number of weekly occurrences, from 2 to 12. The first occurrence is at `start` to `end`, and each one after it is seven calendar days later at the same local time.
- It's all or nothing. If any occurrence breaks a rule or clashes with another booking, nothing is saved, and the response is `409` with a `detail` list that has one entry per failed occurrence: its local `start` and the `reason`, using the same message a single booking would get.
- On success, the response is `201` with `series_id` (a string) and `bookings`, a list of every occurrence in the same shape as `GET /bookings/{id}`.
- Each occurrence is an ordinary booking, so it appears in the schedules and can be moved or cancelled on its own. Store the series in a new, nullable `series_id` column on `bookings`. Existing bookings have no series.
- `DELETE /bookings/series/{series_id}` cancels every occurrence that hasn't started yet and returns `204`. Occurrences that have already started are left alone. An unknown series returns `404`.

## Constraints

- Use `check_slot` for every occurrence. Don't change the booking rules, the clash check, or any existing test.
- Don't add a dependency.
- Keep the route functions thin, and put the series logic in a new module, `roombook/series.py`.

## Acceptance Criteria

1. A four-week series in Midtown (room 10) starting Tuesday 27 October 2026, 10:00 to 11:00, creates bookings on 27 October and on 3, 10, and 17 November, each from 10:00 to 11:00 New York time, even though the clocks change on 1 November.
2. A three-week series in Midtown on Tuesdays from 27 October, 19:00 to 20:00, is rejected with `409`, and the only failed occurrence listed is 3 November, which clashes with the town hall dry run. Nothing is saved.
3. A series whose last occurrence is more than 90 days ahead is rejected with `409`, listing only the occurrences that are too far ahead.
4. `weeks` of 1 or 13 is rejected with `422`.
5. Cancelling a series after its first occurrence has started cancels the later occurrences and leaves the first one as it was.
6. Every existing test still passes, unchanged, and each criterion above has a test.

## Out of Scope

- Other patterns, such as daily, monthly, or every other week.
- Moving or editing a whole series at once.
- Migrating existing databases. Rebuild the sample database with `uv run python -m roombook.seed --reset`.
