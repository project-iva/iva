from __future__ import annotations
import asyncio
from queue import Queue
from threading import Thread

import uuid

from event import Event
from frontend.frontend_socket_server import FrontendSocketServer
from frontend.websocket_message import WebSocketMessage, WebSocketMessageType, WebSocketMessageAction


class EventHandler(Thread):
    def __init__(self, event: Event, iva: Iva, communicator: FrontendSocketServer):
        super().__init__()
        self.event = event
        self.iva = iva
        self.communicator = communicator

    def run(self):
        print(self.event)
        event_loop = asyncio.new_event_loop()
        if self.event.name == 'MORNING':
            print("handling morning")
            event_loop.run_until_complete(self.__handle_morning_routine_event())
            # self.communicator.start_morning_routine()

    async def __handle_morning_routine_event(self):
        for step in range(1, 6):
            data = {
                'step_number': step,
                'steps_count': 5,
                'step': {
                    'title': f'Step {step}',
                    'description': f'Step description'
                }
            }
            message = WebSocketMessage(str(uuid.uuid4()), WebSocketMessageType.REQUEST,
                                       WebSocketMessageAction.MORNING_ROUTINE_UPDATE, data)
            await self.communicator.send_message(message)

        event_queue = Queue()
        self.iva.register_listener('MORNING_CALLBACK', event_queue)
        event = event_queue.get()
        print(f'got response: {event}')
        routine_finished_message = WebSocketMessage(str(uuid.uuid4()), WebSocketMessageType.REQUEST,
                                                    WebSocketMessageAction.MORNING_ROUTINE_FINISHED, {})
        await self.communicator.send_message(routine_finished_message)
