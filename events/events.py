from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional

from interactions.input_provider import InputProvider
from interactions.output_provider import OutputProvider
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
class RaspberryEvent(Event):
    action: RaspberryClient.Action
    data: Optional[dict] = None


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


@dataclass
class RefreshFrontendComponentEvent(Event):
    class Component(str, Enum):
        CALORIES_VIEW = 'CALORIES_VIEW'
        BODY_MASS_VIEW = 'BODY_MASS_VIEW'
        DAY_PLAN_VIEW = 'DAY_PLAN_VIEW'
        DAY_GOALS_VIEW = 'DAY_GOALS_VIEW'
        SLEEP_STATS_VIEW = 'SLEEP_STATS_VIEW'
        MINDFUL_SESSIONS_STATS_VIEW = 'MINDFUL_SESSIONS_STATS_VIEW'

    component: Component


@dataclass
class RefreshDayDataEvent(Event):
    pass


@dataclass
class UtteranceEvent(Event):
    utterance: str
    input_provider: Optional[InputProvider]
    output_provider: Optional[OutputProvider]


@dataclass
class UtteranceIntentEvent(Event):
    class Intent(str, Enum):
        TURN_SCREEN_ON = 'TURN_SCREEN_ON'
        TURN_SCREEN_OFF = 'TURN_SCREEN_OFF'
        INTRODUCE_YOURSELF = 'INTRODUCE_YOURSELF'
        TELL_TIME = 'TELL_TIME'
        SPOTIFY_PLAY = 'SPOTIFY_PLAY'
        SPOTIFY_STOP = 'SPOTIFY_STOP'
        TELL_JOKE = 'TELL_JOKE'

    intent: Intent
    output_provider: Optional[OutputProvider]


@dataclass
class SpotifyEvent(Event):
    class Action(Enum):
        PLAY = auto()
        STOP = auto()

    action: Action
