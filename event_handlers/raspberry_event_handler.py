from queue import Queue
from threading import Thread
from events.events import RaspberryEvent
from raspberry_client.client import RaspberryClient


class RaspberryEventHandler(Thread):
    """
    Forwards raspberry related events to be executed on the raspberry device.
    """

    def __init__(self, event_queue: Queue):
        super().__init__()
        self.event_queue = event_queue

    def run(self):
        while True:
            event: RaspberryEvent = self.event_queue.get()
            print(f'Handling {event}')
            RaspberryClient.send_action_request(event.action, event.data)
