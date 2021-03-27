from websockets import WebSocketServerProtocol

from websocket_message import WebSocketMessage, WebSocketMessageType


class WebsocketMessageHandler:
    def __init__(self, websocket: WebSocketServerProtocol):
        self.websocket = websocket

    async def handle_message(self, message: WebSocketMessage):
        print("handling")
        print(message)
        message.type = WebSocketMessageType.RESPONSE
        response = message.to_json()
        await self.websocket.send(response)
