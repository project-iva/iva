from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Event:
    uuid: UUID = uuid4()


@dataclass
class TimedEvent:
    event: Event
    event_time: datetime

    def __lt__(self, other: TimedEvent):
        return self.event_time < other.event_time


@dataclass
class AwaitedEvent(Event):
    pass


@dataclass
class StartMorningRoutineEvent(Event):
    pass
