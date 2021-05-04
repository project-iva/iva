from queue import Queue
from threading import Thread
from typing import Dict

from event_handler import EventHandler
from frontend.frontend_socket_server import FrontendSocketServer

# TODO: Queue seems like an overkill for an listener, maybe refactor to and threading.Event with extra data
Listener = Dict[str, Queue]


class Iva(Thread):
    def __init__(self, event_queue: Queue, frontend_socket_server: FrontendSocketServer):
        super().__init__()
        self.event_queue = event_queue
        self.frontend_socket_server = frontend_socket_server
        self.listeners: Listener = {}

    def register_listener(self, id: str, queue: Queue):
        self.listeners[id] = queue

    def run(self):
        while True:
            event = self.event_queue.get()
            print(f'iva: {event.name}')
            print(self.listeners.keys())
            if listener := self.listeners.pop(event.name, None):
                print('passing event to a listener')
                listener.put(event)
            else:
                print('starting event handler')
                handler = EventHandler(event, self, self.frontend_socket_server)
                handler.start()
            self.event_queue.task_done()
