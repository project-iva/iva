from __future__ import annotations

import asyncio
from queue import Queue
from threading import Thread
from typing import List

from control_session.session import PresenterSession, PresenterItem, PresenterSessionType, PresenterControlSession, \
    ControllerAction
from events.events import StartRoutineEvent, RoutineType
from websocket.message import WebSocketMessageAction, FrontendWebSocketMessage, \
    RaspberryWebSocketMessage, RaspberrySocketMessageAction
from websocket.server import WebSocketClientType


class StartRoutineEventHandler(Thread):
    def __init__(self, event: StartRoutineEvent, iva: Iva):
        super().__init__()
        self.event = event
        self.iva = iva
        self.event_queue = Queue(1)

    def run(self):
        print(f'Handling {self.event}')
        presenter_session = self.get_presenter_session()

        self.turn_screen_on()

        control_session = PresenterControlSession(presenter_session, self.event_queue, self.iva.socket_server)
        self.iva.register_control_session(control_session)
        control_session.handle_action(ControllerAction.START_PRESENTING)

        # wait for the control session to finish
        self.event_queue.get()
        self.event_queue.task_done()

        self.turn_screen_off()

    def send_routine_message(self, action: WebSocketMessageAction, data: dict):
        message = FrontendWebSocketMessage(action=action, data=data)
        self.iva.socket_server.send_message(message, [WebSocketClientType.WEB_INTERFACE])

    def turn_screen_on(self):
        message = RaspberryWebSocketMessage(action=RaspberrySocketMessageAction.SCREEN_ON)
        self.iva.socket_server.send_message(message, [WebSocketClientType.RASPBERRY])

    def turn_screen_off(self):
        message = RaspberryWebSocketMessage(action=RaspberrySocketMessageAction.SCREEN_OFF)
        self.iva.socket_server.send_message(message, [WebSocketClientType.RASPBERRY])

    def get_presenter_session(self) -> PresenterSession:
        if self.event.type == RoutineType.MORNING:
            items = self.get_morning_routine_items()
        elif self.event.type == RoutineType.EVENING:
            items = self.get_morning_routine_items()
        else:
            raise Exception(f'Unknown routine type {self.event.type}')

        return PresenterSession(PresenterSessionType.ROUTINE, items)

    def get_morning_routine_items(self) -> List[PresenterItem]:
        items = []
        valid_actions = [ControllerAction.NEXT]
        for i in range(5):
            data = {'title': f'Title {i}', 'description': f'Description {i}'}
            item = PresenterItem(data, valid_actions)
            items.append(item)

        data = {'title': f'Last title', 'description': f'Last'}
        item = PresenterItem(data, [ControllerAction.CONFIRM])
        items.append(item)
        return items

    def get_evening_routine_items(self) -> List[PresenterItem]:
        pass
