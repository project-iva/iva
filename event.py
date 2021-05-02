from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:
    name: str


@dataclass
class TimedEvent:
    event: Event
    event_time: datetime

    def __lt__(self, other: TimedEvent):
        return self.event_time < other.event_time
