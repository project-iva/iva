from __future__ import annotations
import asyncio
import uuid
from abc import ABCMeta, abstractmethod
from queue import Queue
from threading import Thread
from typing import Type

from events.events import Event
from websocket.server import WebSocketServer, WebSocketClientType
from websocket.message import WebSocketMessageAction, FrontendWebSocketMessage, WebSocketMessageType, \
    RaspberryWebSocketMessage, RaspberrySocketMessageAction


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

    def wait_for_event_uuid(self, event_uuid: uuid):
        self.iva.register_event_uuid_listener(event_uuid, self.event_queue)
        self.__wait_for_event()

    def wait_for_event_type(self, event_type: Type[Event]):
        self.iva.register_event_type_listener(event_type, self.event_queue)
        self.__wait_for_event()

    def __wait_for_event(self):
        event = self.event_queue.get()
        self.event_queue.task_done()
        print(f'awaited event arrived: {event}')

    def wait_for_event_uuid_or_type(self, event_uuid: uuid, event_type: Type[Event]):
        """
        Waits for either an event with specific uuid or specific type
        Useful for example when an action can be confirmed in several different ways (app/frontend/notification)
        but it does not matter which method was chosen
        """
        self.iva.register_event_uuid_listener(event_uuid, self.event_queue)
        self.iva.register_event_type_listener(event_type, self.event_queue)
        self.__wait_for_event()

        # clean up any possible dangling listeners
        self.iva.unregister_event_uuid_listener(event_uuid)
        self.iva.unregister_event_type_listener(event_type)

    async def send_routine_message(self, action: WebSocketMessageAction, data: dict):
        message = FrontendWebSocketMessage(str(uuid.uuid4()), type=WebSocketMessageType.REQUEST, action=action,
                                           data=data)
        await self.communicator.send_message(message, [WebSocketClientType.WEB_INTERFACE])

    async def turn_screen_on(self):
        message = RaspberryWebSocketMessage(str(uuid.uuid4()), action=RaspberrySocketMessageAction.SCREEN_ON)
        await self.communicator.send_message(message, [WebSocketClientType.RASPBERRY])

    async def turn_screen_off(self):
        message = RaspberryWebSocketMessage(str(uuid.uuid4()), action=RaspberrySocketMessageAction.SCREEN_OFF)
        await self.communicator.send_message(message, [WebSocketClientType.RASPBERRY])

    @abstractmethod
    async def handle(self):
        pass
