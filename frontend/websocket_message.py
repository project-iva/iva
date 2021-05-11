import json
from dataclasses import dataclass, asdict
from enum import Enum


class WebSocketMessageType(str, Enum):
    REQUEST = 'request'
    RESPONSE = 'response'


class WebSocketMessageAction(str, Enum):
    TEST = 'test'
    ECHO = 'echo'
    START_ROUTINE = 'start_routine',
    NEXT_STEP_IN_ROUTINE = 'next_step_in_routine',
    FINISH_ROUTINE = 'finish_routine',


@dataclass
class WebSocketMessage:
    id: str
    type: WebSocketMessageType
    action: WebSocketMessageAction
    data: dict

    @classmethod
    def from_dict(cls, d):
        return cls(
            d.get('id'),
            WebSocketMessageType(d.get('type')),
            WebSocketMessageAction(d.get('action')),
            d.get('data', {})
        )

    @classmethod
    def from_json(cls, j):
        return cls.from_dict(json.loads(j))

    def to_json(self) -> str:
        return json.dumps(asdict(self))
