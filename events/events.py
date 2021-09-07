from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List

from models.day_plan import DayPlanActivity
from raspberry_client.client import RaspberryClient


@dataclass
class Event:
    pass


class RoutineType(str, Enum):
    MORNING = 'MORNING'
    EVENING = 'EVENING'


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
    action: RaspberryClient.Action


@dataclass
class ChooseMealEvent(Event):
    pass


@dataclass
class ChoiceEvent(Event):
    choice: int


@dataclass
class ScheduleDayPlanEvent(Event):
    pass


@dataclass
class DayPlanActivityEvent(Event):
    activity: DayPlanActivity

    def __lt__(self, other: DayPlanActivityEvent):
        return self.activity.start_time < other.activity.start_time


@dataclass
class BackendDataUpdatedEvent(Event):
    class DataType(str, Enum):
        CALORIES = 'CALORIES',
        BODY_MASS = 'BODY_MASS',
        DAY_PLAN = 'DAY_PLAN',
        DAY_GOALS = 'DAY_GOALS',
        SLEEP = 'SLEEP',
        MINDFUL_SESSIONS = 'MINDFUL_SESSIONS',

    data_type: DataType
