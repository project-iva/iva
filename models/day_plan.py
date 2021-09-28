from dataclasses import dataclass
from enum import Enum
from typing import List
from datetime import datetime, date
from models.json_model import JsonModel
import pytz


class DayPlanActivityType(str, Enum):
    MORNING_ROUTINE = 'MORNING_ROUTINE'
    EVENING_ROUTINE = 'EVENING_ROUTINE'
    MEAL = 'MEAL'
    LEISURE = 'LEISURE'
    WORKOUT = 'WORKOUT'
    JOB = 'JOB'
    HOBBY = 'HOBBY'
    OTHER = 'OTHER'


@dataclass
class DayPlanActivity(JsonModel):
    name: str
    description: str
    start_time: datetime
    end_time: datetime
    type: DayPlanActivityType

    @classmethod
    def from_dict(cls, d):
        def convert_string_time_to_datetime(time: str) -> datetime:
            current_date = datetime.now().date()
            ams_tz = pytz.timezone('Europe/Amsterdam')
            # activities come in AMS time
            ams_datetime = ams_tz.localize(datetime.combine(current_date, datetime.strptime(time, '%H:%M:%S').time()))
            # convert to UTC
            utc_datetime = ams_datetime.astimezone(pytz.utc)
            # strip timezone again for easy use
            # TODO: instead of stripping tzinfo, make everything (for example scheduler) timezone aware
            return utc_datetime.replace(tzinfo=None)

        return cls(
            d.get('name'),
            d.get('description'),
            convert_string_time_to_datetime(d.get('start_time')),
            convert_string_time_to_datetime(d.get('end_time')),
            DayPlanActivityType(d.get('type')),
        )


@dataclass
class DayPlan(JsonModel):
    id: int
    date: date
    activities: List[DayPlanActivity]

    @classmethod
    def from_dict(cls, d):
        activities = d.get('activities', [])
        return cls(
            d.get('id'),
            datetime.strptime(d.get('date'), '%Y-%m-%d').date(),
            [DayPlanActivity.from_dict(activity_dict) for activity_dict in activities]
        )
