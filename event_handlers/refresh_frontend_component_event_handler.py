from __future__ import annotations

from queue import Queue
from threading import Thread
from events.events import RefreshFrontendComponentEvent
from websocket.message import FrontendWebSocketMessage, FrontendWebSocketMessageAction
from websocket.server import WebSocketClientType, WebSocketServer


class RefreshFrontendComponentEventHandler(Thread):
    """
    Sends socket message to the frontend, notifying it about which component needs to be refreshed
    """

    def __init__(self, event_queue: Queue, websocket_server: WebSocketServer):
        super().__init__()
        self.event_queue = event_queue
        self.websocket_server = websocket_server

    def run(self):
        while True:
            event: RefreshFrontendComponentEvent = self.event_queue.get()
            print(f'Handling {event}')
            data = {'component_identifier': event.component}
            message = FrontendWebSocketMessage(action=FrontendWebSocketMessageAction.REFRESH_COMPONENT, data=data)
            self.websocket_server.send_message(message, [WebSocketClientType.WEB_INTERFACE])
