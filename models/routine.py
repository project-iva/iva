from dataclasses import dataclass
from typing import List

from models.json_model import JsonModel


@dataclass
class RoutineStep(JsonModel):
    title: str
    description: str
    icon: List[str]
    icon_color: str

    @classmethod
    def from_dict(cls, d):
        return cls(
            d.get('title'),
            d.get('description'),
            d.get('icon'),
            d.get('icon_color'),
        )


@dataclass
class Routine(JsonModel):
    steps: List[RoutineStep]

    @classmethod
    def from_dict(cls, d):
        steps = d.get('steps', [])
        return cls(
            [RoutineStep.from_dict(steps_dict) for steps_dict in steps]
        )
