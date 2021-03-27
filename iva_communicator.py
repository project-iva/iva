import asyncio
from typing import Awaitable

import websockets
from websockets import WebSocketServerProtocol

from websocket_message import WebSocketMessage
from websocket_message_handler import WebsocketMessageHandler


class IvaCommunicator:
    def __init__(self, uri: str, port: int):
        self.__uri = uri
        self.__port = port

    def start(self):
        start_server = websockets.serve(self.__handler, self.__uri, self.__port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def __handler(self, websocket: WebSocketServerProtocol, path: str):
        websocket_message_handler = WebsocketMessageHandler(websocket)
        async for message in websocket:
            websocket_message = WebSocketMessage.from_json(message)
            await websocket_message_handler.handle_message(websocket_message)
