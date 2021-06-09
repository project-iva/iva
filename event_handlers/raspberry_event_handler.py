import asyncio
from threading import Thread
import uuid
from events.events import RaspberryEvent, TurnRaspberryScreenOnEvent, TurnRaspberryScreenOffEvent
from websocket.message import RaspberrySocketMessageAction, RaspberryWebSocketMessage
from websocket.server import WebSocketServer, WebSocketClientType


class RaspberryEventHandler(Thread):
    def __init__(self, raspberry_event: RaspberryEvent, websocket_server: WebSocketServer):
        super().__init__()
        self.raspberry_event = raspberry_event
        self.websocket_server = websocket_server
        self.action_mapping = {
            TurnRaspberryScreenOnEvent: RaspberrySocketMessageAction.SCREEN_ON,
            TurnRaspberryScreenOffEvent: RaspberrySocketMessageAction.SCREEN_OFF,
        }

    def run(self):
        print(f'Handling {self.raspberry_event}')
        event_loop = asyncio.new_event_loop()
        event_loop.run_until_complete(self.handle())

    async def handle(self):
        action = self.action_mapping[type(self.raspberry_event)]

        message = RaspberryWebSocketMessage(str(uuid.uuid4()), action=action)
        await self.websocket_server.send_message(message, [WebSocketClientType.RASPBERRY])
