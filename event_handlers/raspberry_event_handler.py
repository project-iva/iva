from threading import Thread
from events.events import RaspberryEvent
from raspberry_client.client import RaspberryClient


class RaspberryEventHandler(Thread):
    def __init__(self, raspberry_event: RaspberryEvent):
        super().__init__()
        self.raspberry_event = raspberry_event

    def run(self):
        print(f'Handling {self.raspberry_event}')
        RaspberryClient.send_action_request(self.raspberry_event.action, self.raspberry_event.data)
