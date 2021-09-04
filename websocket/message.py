from abc import ABCMeta
from dataclasses import dataclass
from enum import Enum

from models.json_model import JsonEncodableModel


class FrontendWebSocketMessageAction(str, Enum):
    START_PRESENTER = 'start_presenter'
    NEXT_ITEM_IN_PRESENTER = 'next_item_in_presenter'
    PREV_ITEM_IN_PRESENTER = 'prev_item_in_presenter'
    PRESENTER_FINISHED = 'presenter_finished'


@dataclass
class FrontendWebSocketMessage(JsonEncodableModel):
    action: FrontendWebSocketMessageAction
    data: dict
