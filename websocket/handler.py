from websockets import WebSocketServerProtocol

from websocket.message import WebsocketMessage


class WebSocketConnectionHandler:
    def __init__(self, websocket: WebSocketServerProtocol):
        self.websocket = websocket

    async def send_message(self, message: WebsocketMessage):
        print(f"sending: {message}")
        await self.websocket.send(message.json)
