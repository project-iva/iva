import uuid as uuid
from websockets import WebSocketServerProtocol

from websocket.message import FrontendWebSocketMessage, WebSocketMessageType, WebSocketMessageAction, WebsocketMessage


class WebSocketConnectionHandler:
    def __init__(self, websocket: WebSocketServerProtocol):
        self.websocket = websocket
        self.__dispatcher = {
            WebSocketMessageAction.ECHO: self.__echo_action,
            WebSocketMessageAction.TEST: self.__test_action,
        }

    async def handle_message(self, message: FrontendWebSocketMessage):
        print(f"handling: {message}")
        await self.__dispatcher[message.action](message)

    async def send_message(self, message: WebsocketMessage):
        print(f"sending: {message}")
        await self.websocket.send(message.to_json())

    async def __echo_action(self, message: FrontendWebSocketMessage):
        message.type = WebSocketMessageType.RESPONSE
        print(f"echoing: {message}")
        await self.websocket.send(message.to_json())

    async def __test_action(self, message: FrontendWebSocketMessage):
        test_data = {
            'key': 'value'
        }
        message = FrontendWebSocketMessage(str(uuid.uuid4()), WebSocketMessageType.REQUEST, WebSocketMessageAction.TEST, test_data)
        await self.websocket.send(message.to_json())
