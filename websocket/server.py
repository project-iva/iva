import asyncio
from enum import Enum
from threading import Thread
from typing import List, Dict, Optional

import websockets
from websockets import WebSocketServerProtocol

from websocket.message import FrontendWebSocketMessage, WebsocketMessage
from websocket.handler import WebSocketConnectionHandler


class WebSocketClientType(str, Enum):
    WEB_INTERFACE = 'web'
    APP = 'ios'


# TODO: switch to autobahn package to avoid dealing with asyncio
class WebSocketServer(Thread):
    def __init__(self, uri: str, port: int):
        super().__init__()
        self.__uri = uri
        self.__port = port
        self.__connected_clients: Dict[WebSocketClientType, List[WebSocketConnectionHandler]] = {
            WebSocketClientType.WEB_INTERFACE: [],
            WebSocketClientType.APP: []
        }

    def run(self):
        server_loop = asyncio.new_event_loop()
        start_server = websockets.serve(self.__handler, self.__uri, self.__port, loop=server_loop)
        server_loop.run_until_complete(start_server)
        server_loop.run_forever()

    async def __handler(self, websocket: WebSocketServerProtocol, path: str):
        websocket_connection_handler = WebSocketConnectionHandler(websocket)
        # get rid of the prefixed slash and get type
        connection_type = WebSocketClientType(path[1:])
        print(f'new connection; type: {connection_type}')
        self.__connected_clients[connection_type].append(websocket_connection_handler)
        async for message in websocket:
            websocket_message = FrontendWebSocketMessage.from_json(message)
            await websocket_connection_handler.handle_message(websocket_message)

        # iteration terminates when the client disconnects
        self.__connected_clients[connection_type].remove(websocket_connection_handler)

    async def send_message(self, message: WebsocketMessage, client_types: Optional[List[WebSocketClientType]] = None):
        if client_types is None:
            client_types = [WebSocketClientType.WEB_INTERFACE, WebSocketClientType.APP]

        coroutines = []
        for client_type in client_types:
            for handler in self.__connected_clients[client_type]:
                coroutines.append(handler.send_message(message))
        await asyncio.gather(*coroutines)
