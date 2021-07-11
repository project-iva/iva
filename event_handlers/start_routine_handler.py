from __future__ import annotations
from queue import Queue
from threading import Thread
from typing import List

from control_session.session import PresenterSession, PresenterItem, PresenterSessionType, PresenterControlSession, \
    ControllerAction
from events.events import StartRoutineEvent, RoutineType
from models.routine import RoutineStep
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
        routine_steps = [
            RoutineStep('Water', 'Drink a glass of water', ['fas', 'glass-whiskey'], 'LightSkyBlue'),
            RoutineStep('Mindfulness', 'Meditation', ['fas', 'brain'], 'SlateGrey'),
            RoutineStep('TODOs', 'Prepare a list of TODOs for the day', ['fas', 'list'], 'DarkGray'),
            RoutineStep('Journal', 'Write/sketch for a few minutes', ['fas', 'journal-whills'], 'Maroon'),
        ]

        return self.get_presenter_items(routine_steps)

    def get_evening_routine_items(self) -> List[PresenterItem]:
        routine_steps = [
            RoutineStep('Reading', 'Read a book for a few minutes', ['fas', 'book'], 'Sienna'),
            RoutineStep('Journal', 'Write/sketch for a few minutes', ['fas', 'journal-whills'], 'Maroon'),
            RoutineStep('Mindfulness', 'Meditation', ['fas', 'brain'], 'SlateGrey'),
        ]

        return self.get_presenter_items(routine_steps)

    def get_presenter_items(self, routine_steps: List[RoutineStep]) -> List[PresenterItem]:
        presenter_items = []
        last_step_index = len(routine_steps) - 1

        for index, step in enumerate(routine_steps):
            if index == last_step_index:
                item = PresenterItem(step.dict, [ControllerAction.CONFIRM])
            else:
                item = PresenterItem(step.dict, [ControllerAction.NEXT])
            presenter_items.append(item)

        return presenter_items
