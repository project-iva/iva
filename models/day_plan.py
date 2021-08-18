from dataclasses import dataclass
from enum import Enum
from typing import List
from datetime import datetime, date
from models.json_model import JsonModel


class DayPlanActivityType(str, Enum):
    MORNING_ROUTINE = 'MORNING_ROUTINE'
    EVENING_ROUTINE = 'EVENING_ROUTINE'
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
            return datetime.combine(current_date, datetime.strptime(time, '%H:%M:%S').time())

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
