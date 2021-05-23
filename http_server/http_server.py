import socketserver
from collections import deque
from http.server import BaseHTTPRequestHandler, HTTPServer
from queue import Empty, Queue
from typing import Tuple, List

from uuid import UUID

from events.events import MindfulSessionRecordedEvent, AwaitedEvent, Event


class PostHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer):
        self.post_dispatcher = {
            '/next': self.handle_next,
            '/mindful_session_recorded': self.handle_mindful_session_recorded
        }

        super().__init__(request, client_address, server)

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        try:
            print(f'Handling POST to {self.path}')
            self.post_dispatcher[self.path]()
        except KeyError:
            print(f'Invalid path: {self.path}')

    def handle_next(self):
        print('Handling POST to /next')
        try:
            awaited_uuid = self.server.awaited_event_uuids.popleft()
            self.server.event_queue.put(AwaitedEvent(Event(awaited_uuid)))
        except IndexError:
            pass

    def handle_mindful_session_recorded(self):
        print('Handling POST to /next')
        awaited_event = AwaitedEvent(MindfulSessionRecordedEvent())
        self.server.event_queue.put(awaited_event)


class SimpleHTTPServer(HTTPServer):
    def __init__(self, awaited_event_uuids: deque, event_queue: Queue):
        super().__init__(('0.0.0.0', 8001), PostHTTPRequestHandler)
        self.awaited_event_uuids = awaited_event_uuids
        self.event_queue = event_queue
