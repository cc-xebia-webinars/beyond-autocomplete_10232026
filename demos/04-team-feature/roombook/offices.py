"""The offices Roombook serves, and the time zone each one keeps."""

from dataclasses import dataclass
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class Office:
    code: str
    name: str
    tz: ZoneInfo


OFFICES: dict[str, Office] = {
    "AMS": Office("AMS", "Amsterdam", ZoneInfo("Europe/Amsterdam")),
    "NYC": Office("NYC", "New York", ZoneInfo("America/New_York")),
}
