from __future__ import annotations
import asyncio
from queue import Queue
from threading import Thread

import uuid

from events.events import Event
from frontend.frontend_socket_server import FrontendSocketServer
from frontend.websocket_message import WebSocketMessage, WebSocketMessageType, WebSocketMessageAction


class EventHandler(Thread):
    def __init__(self, event: Event, iva: Iva, communicator: FrontendSocketServer):
        super().__init__()
        self.event = event
        self.iva = iva
        self.communicator = communicator
        self.event_queue = Queue(1)

    def run(self):
        print(self.event)
        event_loop = asyncio.new_event_loop()
        event_loop.run_until_complete(self.__handle_morning_routine_event())

    def __wait_for_confirmation(self):
        self.iva.register_listener(uuid.uuid4(), self.event_queue)
        event = self.event_queue.get()
        self.event_queue.task_done()
        print(f'got response: {event}')

    async def __send_routine_message(self, action: WebSocketMessageAction, data: dict):
        message = WebSocketMessage(str(uuid.uuid4()), WebSocketMessageType.REQUEST, action, data)
        await self.communicator.send_message(message)

    async def __handle_morning_routine_event(self):

        start_routine_data = {
            'routine_name': 'morning_routine'
        }
        await self.__send_routine_message(WebSocketMessageAction.START_ROUTINE, start_routine_data)
        self.__wait_for_confirmation()

        for step in range(2):
            await self.__send_routine_message(WebSocketMessageAction.NEXT_STEP_IN_ROUTINE, {})
            self.__wait_for_confirmation()

        await self.__send_routine_message(WebSocketMessageAction.FINISH_ROUTINE, {})
