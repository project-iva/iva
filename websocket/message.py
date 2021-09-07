from dataclasses import dataclass
from enum import Enum

from models.json_model import JsonEncodableModel


class FrontendWebSocketMessageAction(str, Enum):
    START_PRESENTER = 'START_PRESENTER'
    NEXT_ITEM_IN_PRESENTER = 'NEXT_ITEM_IN_PRESENTER'
    PREV_ITEM_IN_PRESENTER = 'PREV_ITEM_IN_PRESENTER'
    PRESENTER_FINISHED = 'PRESENTER_FINISHED'
    REFRESH_COMPONENT = 'REFRESH_COMPONENT'


@dataclass
class FrontendWebSocketMessage(JsonEncodableModel):
    action: FrontendWebSocketMessageAction
    data: dict
