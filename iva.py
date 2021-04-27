from queue import Queue
from threading import Thread
from typing import Dict

from event_handler import EventHandler
from iva_communicator import IvaCommunicator

# TODO: Queue seems like an overkill for an listener, maybe refactor to and threading.Event with extra data
Listener = Dict[str, Queue]


class Iva(Thread):
    def __init__(self, event_queue: Queue, communicator: IvaCommunicator):
        super().__init__()
        self.event_queue = event_queue
        self.communicator = communicator
        self.listeners: Listener = {}

    def register_listener(self, id: str, queue: Queue):
        self.listeners[id] = queue

    def run(self):
        while True:
            event = self.event_queue.get()
            print(f'iva: {event}')
            print(self.listeners.keys())
            if listener := self.listeners.pop(event, None):
                print('passing event to a listener')
                listener.put(event)
            else:
                print('starting event handler')
                handler = EventHandler(event, self, self.communicator)
                handler.start()
            self.event_queue.task_done()
