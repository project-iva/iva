import asyncio
from threading import Thread
from typing import List

import websockets
from websockets import WebSocketServerProtocol

from websocket_message import WebSocketMessage
from websocket_message_handler import WebsocketMessageHandler


class IvaCommunicator(Thread):
    def __init__(self, uri: str, port: int):
        super().__init__()
        self.__uri = uri
        self.__port = port
        self.__connected_sockets: List[WebsocketMessageHandler] = []

    def run(self):
        server_loop = asyncio.new_event_loop()
        start_server = websockets.serve(self.__handler, self.__uri, self.__port, loop=server_loop)
        server_loop.run_until_complete(start_server)
        server_loop.run_forever()

    async def __handler(self, websocket: WebSocketServerProtocol, path: str):
        websocket_message_handler = WebsocketMessageHandler(websocket)
        self.__connected_sockets.append(websocket_message_handler)
        async for message in websocket:
            websocket_message = WebSocketMessage.from_json(message)
            await websocket_message_handler.handle_message(websocket_message)

    async def send_message(self, message: WebSocketMessage):
        coroutines = [handler.send_message(message) for handler in self.__connected_sockets]
        await asyncio.gather(*coroutines)
