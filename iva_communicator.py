import asyncio
from typing import Awaitable

import websockets
from websockets import WebSocketServerProtocol


class IvaCommunicator:
    def __init__(self, uri: str, port: int):
        self.__uri = uri
        self.__port = port

    def start(self):
        start_server = websockets.serve(self.__handler, self.__uri, self.__port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def __handler(self, websocket: WebSocketServerProtocol, path: str):
        async for message in websocket:
            print(message)
