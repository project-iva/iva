from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


@dataclass
class Event:
    pass


class RoutineType(str, Enum):
    MORNING = 'morning'
    EVENING = 'evening'


@dataclass
class StartRoutineEvent(Event):
    type: RoutineType


@dataclass
class MindfulSessionRecordedEvent(Event):
    pass


@dataclass
class CommandEvent(Event):
    command: str
    args: List[str]


@dataclass
class UtteranceEvent(Event):
    utterance: str


@dataclass
class RaspberryEvent(Event):
    pass


@dataclass
class TurnRaspberryScreenOnEvent(RaspberryEvent):
    pass


@dataclass
class TurnRaspberryScreenOffEvent(RaspberryEvent):
    pass


@dataclass
class ChooseMealEvent(Event):
    pass


@dataclass
class ChoiceEvent(Event):
    choice: int
