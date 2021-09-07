from __future__ import annotations
from threading import Thread
from events.events import BackendDataUpdatedEvent


class BackendDataUpdatedEventHandler(Thread):
    def __init__(self, data_updated_event: BackendDataUpdatedEvent, iva: Iva):
        super().__init__()
        self.data_updated_event = data_updated_event

    def run(self):
        print(f'Handling {self.data_updated_event}')
