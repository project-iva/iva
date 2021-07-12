import asyncio
from enum import Enum
from threading import Thread
from typing import List, Dict, Optional

import websockets
from websockets import WebSocketServerProtocol

from websocket.handler import WebSocketConnectionHandler
from websocket.message import WebsocketMessage


class WebSocketClientType(str, Enum):
    WEB_INTERFACE = 'web'
    RASPBERRY = 'raspberry'


# TODO: switch to autobahn package to avoid dealing with asyncio
class WebSocketServer(Thread):
    def __init__(self, uri: str, port: int):
        super().__init__()
        self.__uri = uri
        self.__port = port
        self.__connected_clients = self.__create_clients_mapping()

    def __create_clients_mapping(self) -> Dict[WebSocketClientType, List[WebSocketConnectionHandler]]:
        clients: Dict[WebSocketClientType, List[WebSocketConnectionHandler]] = {}
        # initialize client list for all possible connection types
        for client_type in list(WebSocketClientType):
            clients[client_type] = []
        return clients

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
        async for _ in websocket:
            pass

        # iteration terminates when the client disconnects
        self.__connected_clients[connection_type].remove(websocket_connection_handler)

    def send_message(self, message: WebsocketMessage, client_types: Optional[List[WebSocketClientType]] = None):
        if client_types is None:
            client_types = list(WebSocketClientType)

        coroutines = []
        for client_type in client_types:
            for handler in self.__connected_clients[client_type]:
                coroutines.append(handler.send_message(message))

        event_loop = asyncio.new_event_loop()
        feature = asyncio.gather(*coroutines, loop=event_loop)
        event_loop.run_until_complete(feature)
