from __future__ import annotations
from queue import Queue
from threading import Thread
from typing import List

from control_session.session import PresenterSession, PresenterItem, PresenterSessionType, PresenterControlSession, \
    ControlSessionAction
from events.events import StartRoutineEvent, RoutineType, RaspberryEvent
from models.routine import RoutineStep
from raspberry_client.client import RaspberryClient


class StartRoutineEventHandler(Thread):
    """
    Handles start routine event by showing presenter in the frontend and creating a control session to handle user input
    """

    def __init__(self, event_queue: Queue, iva: Iva):
        super().__init__()
        self.event_queue = event_queue
        self.iva = iva

    def run(self):
        while True:
            event: StartRoutineEvent = self.event_queue.get()
            print(f'Handling {event}')
            presenter_session = self.__get_presenter_session(event)

            self.__turn_screen_on()
            control_session_event_queue = Queue(1)
            control_session = PresenterControlSession(presenter_session, control_session_event_queue,
                                                      self.iva.socket_server)
            session_uuid = self.iva.register_control_session(control_session)
            control_session.handle_action(ControlSessionAction.START_PRESENTING)

            # wait for the control session to finish
            control_session_event_queue.get()
            control_session_event_queue.task_done()
            self.iva.unregister_control_session(session_uuid)

            self.__turn_screen_off()

    def __turn_screen_on(self):
        self.iva.event_scheduler.schedule_event(RaspberryEvent(RaspberryClient.Action.SCREEN_ON))

    def __turn_screen_off(self):
        self.iva.event_scheduler.schedule_event(RaspberryEvent(RaspberryClient.Action.SCREEN_OFF))

    def __get_presenter_session(self, event: StartRoutineEvent) -> PresenterSession:
        if event.type == RoutineType.MORNING:
            items = self.__get_morning_routine_items()
        elif event.type == RoutineType.EVENING:
            items = self.__get_evening_routine_items()
        else:
            raise Exception(f'Unknown routine type {event.type}')

        return PresenterSession(PresenterSessionType.ROUTINE, items)

    def __get_morning_routine_items(self) -> List[PresenterItem]:
        routine_steps = [
            RoutineStep('Water', 'Drink a glass of water', ['fas', 'glass-whiskey'], 'LightSkyBlue'),
            RoutineStep('Mindfulness', 'Meditation', ['fas', 'brain'], 'SlateGrey'),
            RoutineStep('TODOs', 'Prepare a list of TODOs for the day', ['fas', 'list'], 'DarkGray'),
            RoutineStep('Journal', 'Write/sketch for a few minutes', ['fas', 'journal-whills'], 'Maroon'),
        ]

        return self.__get_presenter_items(routine_steps)

    def __get_evening_routine_items(self) -> List[PresenterItem]:
        routine_steps = [
            RoutineStep('Reading', 'Read a book for a few minutes', ['fas', 'book'], 'Sienna'),
            RoutineStep('Journal', 'Write/sketch for a few minutes', ['fas', 'journal-whills'], 'Maroon'),
            RoutineStep('Mindfulness', 'Meditation', ['fas', 'brain'], 'SlateGrey'),
        ]

        return self.__get_presenter_items(routine_steps)

    def __get_presenter_items(self, routine_steps: List[RoutineStep]) -> List[PresenterItem]:
        presenter_items = []
        last_step_index = len(routine_steps) - 1

        for index, step in enumerate(routine_steps):
            if index == last_step_index:
                item = PresenterItem(step.dict, [ControlSessionAction.CONFIRM])
            else:
                item = PresenterItem(step.dict, [ControlSessionAction.NEXT])
            presenter_items.append(item)

        return presenter_items
