from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass
class Event:
    uuid: UUID = uuid4()


@dataclass
class AwaitedEvent(Event):
    pass


@dataclass
class StartMorningRoutineEvent(Event):
    pass
