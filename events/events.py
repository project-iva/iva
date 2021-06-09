from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass
class Event:
    uuid: UUID = uuid4()


@dataclass
class AwaitedEvent:
    event: Event


@dataclass
class StartMorningRoutineEvent(Event):
    pass


@dataclass
class StartEveningRoutineEvent(Event):
    pass


@dataclass
class MindfulSessionRecordedEvent(Event):
    pass


@dataclass
class CommandEvent(Event):
    command: str = ""


@dataclass
class UtteranceEvent(Event):
    utterance: str = ""


@dataclass
class RaspberryEvent(Event):
    pass


@dataclass
class TurnRaspberryScreenOnEvent(RaspberryEvent):
    pass


@dataclass
class TurnRaspberryScreenOffEvent(RaspberryEvent):
    pass
