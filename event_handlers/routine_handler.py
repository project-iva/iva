from __future__ import annotations
import asyncio
import uuid
from abc import ABCMeta, abstractmethod
from queue import Queue
from threading import Thread

from events.events import Event
from websocket.server import WebSocketServer
from websocket.message import WebSocketMessageAction, FrontendWebSocketMessage, WebSocketMessageType


class RoutineEventHandler(Thread, metaclass=ABCMeta):
    def __init__(self, event: Event, iva: Iva, communicator: WebSocketServer):
        super().__init__()
        self.event = event
        self.iva = iva
        self.communicator = communicator
        self.event_queue = Queue(1)

    def run(self):
        print(self.event)
        event_loop = asyncio.new_event_loop()
        event_loop.run_until_complete(self.handle())

    def wait_for_confirmation(self):
        self.iva.register_listener(uuid.uuid4(), self.event_queue)
        event = self.event_queue.get()
        self.event_queue.task_done()
        print(f'got response: {event}')

    async def send_routine_message(self, action: WebSocketMessageAction, data: dict):
        message = FrontendWebSocketMessage(str(uuid.uuid4()), type=WebSocketMessageType.REQUEST, action=action,
                                           data=data)
        await self.communicator.send_message(message)

    @abstractmethod
    async def handle(self):
        pass
