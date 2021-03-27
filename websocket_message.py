import json
from dataclasses import dataclass, asdict
from enum import Enum


class WebSocketMessageType(str, Enum):
    REQUEST = 'request'
    RESPONSE = 'response'


class WebSocketMessageAction(str, Enum):
    TEST = 'test'
    ECHO = 'echo'


@dataclass
class WebSocketMessage:
    id: int
    type: WebSocketMessageType
    action: WebSocketMessageAction
    data: dict

    @classmethod
    def from_dict(cls, d):
        return cls(d['id'], WebSocketMessageType(d['type']), WebSocketMessageAction(d['action']), d['data'])

    @classmethod
    def from_json(cls, j):
        return cls.from_dict(json.loads(j))

    def to_json(self) -> str:
        return json.dumps(asdict(self))
