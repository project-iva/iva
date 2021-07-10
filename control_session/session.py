import asyncio
from dataclasses import dataclass
from dataclasses import dataclass
from enum import Enum
from queue import Queue
from typing import List

from json_model import JsonEncodableModel
from websocket.message import FrontendWebSocketMessage, WebSocketMessageAction
from websocket.server import WebSocketClientType, WebSocketServer


class InvalidControlActionException(Exception):
    pass


class ControllerAction(str, Enum):
    START_PRESENTING = 'start_presenting'
    NEXT = 'next'
    PREV = 'prev'
    CONFIRM = 'confirm'


@dataclass
class PresenterItem:
    data: dict
    valid_actions: List[ControllerAction]


class PresenterSessionType(str, Enum):
    ROUTINE = 'routine'
    MEAL_CHOICES = 'meal_choices'


@dataclass
class PresenterSession(JsonEncodableModel):
    session_type: PresenterSessionType
    steps: List[PresenterItem]


class PresenterControlSession:
    def __init__(self, presenter_session: PresenterSession, queue: Queue, socket_server: WebSocketServer):
        self.presenter_session = presenter_session
        self.queue = queue
        self.current_item = 0
        self.socket_server = socket_server
        self.event_loop = asyncio.new_event_loop()

    def handle_action(self, action: ControllerAction):
        dispatcher = {
            ControllerAction.NEXT: self.perform_next_action,
            ControllerAction.PREV: self.perform_prev_action,
            ControllerAction.CONFIRM: self.perform_confirm_action,
            ControllerAction.START_PRESENTING: self.start_presenting,
        }

        presenter_step = self.presenter_session.steps[self.current_item]
        if action == ControllerAction.START_PRESENTING or action in presenter_step.valid_actions:
            dispatcher[action]()
        else:
            raise InvalidControlActionException

    def start_presenting(self):
        data = self.presenter_session.dict
        message = FrontendWebSocketMessage(action=WebSocketMessageAction.START_PRESENTER, data=data)
        self.socket_server.send_message(message, [WebSocketClientType.WEB_INTERFACE])

    def perform_next_action(self):
        self.current_item += 1
        data = {'session_type': PresenterSessionType.MEAL_CHOICES}
        message = FrontendWebSocketMessage(action=WebSocketMessageAction.NEXT_ITEM_IN_PRESENTER, data=data)
        self.socket_server.send_message(message, [WebSocketClientType.WEB_INTERFACE])

    def perform_prev_action(self):
        self.current_item -= 1
        data = {'session_type': PresenterSessionType.MEAL_CHOICES}
        message = FrontendWebSocketMessage(action=WebSocketMessageAction.PREV_ITEM_IN_PRESENTER, data=data)
        self.socket_server.send_message(message, [WebSocketClientType.WEB_INTERFACE])

    def perform_confirm_action(self):
        data = {'session_type': PresenterSessionType.MEAL_CHOICES}
        message = FrontendWebSocketMessage(action=WebSocketMessageAction.PRESENTER_FINISHED, data=data)
        self.socket_server.send_message(message, [WebSocketClientType.WEB_INTERFACE])
        self.queue.put(self.current_item)
