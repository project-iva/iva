from abc import ABCMeta
from dataclasses import dataclass
from enum import Enum

from models.json_model import JsonEncodableModel


class WebSocketMessageAction(str, Enum):
    START_PRESENTER = 'start_presenter'
    NEXT_ITEM_IN_PRESENTER = 'next_item_in_presenter'
    PREV_ITEM_IN_PRESENTER = 'prev_item_in_presenter'
    PRESENTER_FINISHED = 'presenter_finished'


class RaspberrySocketMessageAction(str, Enum):
    SCREEN_ON = 'screen_on'
    SCREEN_OFF = 'screen_off'


@dataclass
class WebsocketMessage(JsonEncodableModel, metaclass=ABCMeta):
    pass


@dataclass
class FrontendWebSocketMessage(WebsocketMessage):
    action: WebSocketMessageAction
    data: dict


@dataclass
class RaspberryWebSocketMessage(WebsocketMessage):
    action: RaspberrySocketMessageAction
