from abc import ABCMeta
from dataclasses import dataclass
from enum import Enum

from json_model import JsonModel


class WebSocketMessageType(str, Enum):
    REQUEST = 'request'
    RESPONSE = 'response'


class WebSocketMessageAction(str, Enum):
    TEST = 'test'
    ECHO = 'echo'
    START_ROUTINE = 'start_routine',
    NEXT_STEP_IN_ROUTINE = 'next_step_in_routine',
    FINISH_ROUTINE = 'finish_routine',


class RaspberrySocketMessageAction(str, Enum):
    SCREEN_ON = 'screen_on'
    SCREEN_OFF = 'screen_off'


@dataclass
class WebsocketMessage(JsonModel, metaclass=ABCMeta):
    id: str


@dataclass
class FrontendWebSocketMessage(WebsocketMessage):
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


@dataclass
class RaspberryWebSocketMessage(WebsocketMessage):
    action: RaspberrySocketMessageAction

    @classmethod
    def from_dict(cls, d):
        return cls(
            d.get('id'),
            RaspberrySocketMessageAction(d.get('action')),
        )
