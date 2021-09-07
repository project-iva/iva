from __future__ import annotations
from threading import Thread
from events.events import RefreshFrontendComponentEvent
from websocket.message import FrontendWebSocketMessage, FrontendWebSocketMessageAction
from websocket.server import WebSocketClientType


class RefreshFrontendComponentEventHandler(Thread):
    def __init__(self, refresh_frontend_component_event: RefreshFrontendComponentEvent, iva: Iva):
        super().__init__()
        self.refresh_frontend_component_event = refresh_frontend_component_event
        self.iva = iva

    def run(self):
        print(f'Handling {self.refresh_frontend_component_event}')
        data = {'component_identifier': self.refresh_frontend_component_event.component}
        message = FrontendWebSocketMessage(action=FrontendWebSocketMessageAction.REFRESH_COMPONENT, data=data)
        self.iva.socket_server.send_message(message, [WebSocketClientType.WEB_INTERFACE])
