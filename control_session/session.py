import asyncio
from dataclasses import dataclass
from enum import Enum
from queue import Queue
from typing import List

from models.json_model import JsonEncodableModel
from websocket.message import FrontendWebSocketMessage, FrontendWebSocketMessageAction
from websocket.server import WebSocketClientType, WebSocketServer


class InvalidControlSessionActionException(Exception):
    pass


class ControlSessionAction(str, Enum):
    START_PRESENTING = 'START_PRESENTING'
    NEXT = 'NEXT'
    PREV = 'PREV'
    CONFIRM = 'CONFIRM'


@dataclass
class PresenterItem:
    data: dict
    valid_actions: List[ControlSessionAction]


class PresenterSessionType(str, Enum):
    ROUTINE = 'ROUTINE'
    MEAL_CHOICES = 'MEAL_CHOICES'


@dataclass
class PresenterSession(JsonEncodableModel):
    session_type: PresenterSessionType
    items: List[PresenterItem]


class PresenterControlSession:
    def __init__(self, presenter_session: PresenterSession, queue: Queue, socket_server: WebSocketServer):
        self.presenter_session = presenter_session
        self.queue = queue
        self.current_item = 0
        self.socket_server = socket_server
        self.event_loop = asyncio.new_event_loop()

    def handle_action(self, action: ControlSessionAction):
        dispatcher = {
            ControlSessionAction.NEXT: self.perform_next_action,
            ControlSessionAction.PREV: self.perform_prev_action,
            ControlSessionAction.CONFIRM: self.perform_confirm_action,
            ControlSessionAction.START_PRESENTING: self.start_presenting,
        }

        presenter_step = self.presenter_session.items[self.current_item]
        if action == ControlSessionAction.START_PRESENTING or action in presenter_step.valid_actions:
            dispatcher[action]()
        else:
            raise InvalidControlSessionActionException

    def start_presenting(self):
        data = self.presenter_session.dict
        message = FrontendWebSocketMessage(action=FrontendWebSocketMessageAction.START_PRESENTER, data=data)
        self.socket_server.send_message(message, [WebSocketClientType.WEB_INTERFACE])

    def perform_next_action(self):
        self.current_item += 1
        data = {'session_type': self.presenter_session.session_type}
        message = FrontendWebSocketMessage(action=FrontendWebSocketMessageAction.NEXT_ITEM_IN_PRESENTER, data=data)
        self.socket_server.send_message(message, [WebSocketClientType.WEB_INTERFACE])

    def perform_prev_action(self):
        self.current_item -= 1
        data = {'session_type': self.presenter_session.session_type}
        message = FrontendWebSocketMessage(action=FrontendWebSocketMessageAction.PREV_ITEM_IN_PRESENTER, data=data)
        self.socket_server.send_message(message, [WebSocketClientType.WEB_INTERFACE])

    def perform_confirm_action(self):
        data = {'session_type': self.presenter_session.session_type}
        message = FrontendWebSocketMessage(action=FrontendWebSocketMessageAction.PRESENTER_FINISHED, data=data)
        self.socket_server.send_message(message, [WebSocketClientType.WEB_INTERFACE])
        self.queue.put(self.current_item)
