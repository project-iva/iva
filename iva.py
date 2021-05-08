from queue import Queue
from threading import Thread
from typing import Dict

from uuid import UUID

from event_handler import EventHandler
from events.events import AwaitedEvent, StartMorningRoutineEvent
from frontend.frontend_socket_server import FrontendSocketServer

# TODO: Queue seems like an overkill for an listener, maybe refactor to and threading.Event with extra data
Listener = Dict[UUID, Queue]


class Iva(Thread):
    def __init__(self, event_queue: Queue, awaited_event_queue: Queue, frontend_socket_server: FrontendSocketServer):
        super().__init__()
        self.event_queue = event_queue
        self.awaited_event_queue = awaited_event_queue
        self.frontend_socket_server = frontend_socket_server
        self.listeners: Listener = {}
        self.dispatcher = {
            AwaitedEvent: self.__handle_awaited_event,
            StartMorningRoutineEvent: self.__handle_start_morning_routine_event
        }

    def register_listener(self, uuid: UUID, queue: Queue):
        self.listeners[uuid] = queue
        self.awaited_event_queue.put(AwaitedEvent(uuid))

    def run(self):
        while True:
            event = self.event_queue.get()
            self.dispatcher[type(event)](event)
            self.event_queue.task_done()

    def __handle_awaited_event(self, awaited_event: AwaitedEvent):
        if listener := self.listeners.pop(awaited_event.uuid, None):
            print('passing event to a listener')
            listener.put(awaited_event)

    def __handle_start_morning_routine_event(self, start_morning_routine_event: StartMorningRoutineEvent):
        handler = EventHandler(start_morning_routine_event, self, self.frontend_socket_server)
        handler.start()
