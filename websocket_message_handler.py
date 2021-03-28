import uuid as uuid
from websockets import WebSocketServerProtocol

from websocket_message import WebSocketMessage, WebSocketMessageType, WebSocketMessageAction


class WebsocketMessageHandler:
    def __init__(self, websocket: WebSocketServerProtocol):
        self.websocket = websocket
        self.__dispatcher = {
            WebSocketMessageAction.ECHO: self.__echo_action,
            WebSocketMessageAction.TEST: self.__test_action,
        }

    async def handle_message(self, message: WebSocketMessage):
        print(f"handling: {message}")
        await self.__dispatcher[message.action](message)

    async def __echo_action(self, message: WebSocketMessage):
        message.type = WebSocketMessageType.RESPONSE
        print(f"echoing: {message}")
        await self.websocket.send(message.to_json())

    async def __test_action(self, message: WebSocketMessage):
        test_data = {
            'key': 'value'
        }
        message = WebSocketMessage(str(uuid.uuid4()), WebSocketMessageType.REQUEST, WebSocketMessageAction.TEST, test_data)
        await self.websocket.send(message.to_json())
