from http.server import BaseHTTPRequestHandler, HTTPServer
from queue import Empty, Queue


class PostHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        print("POST")
        try:
            event = self.server.awaited_event_queue.get(False)
            self.server.event_queue.put(event)
        except Empty:
            pass


class SimpleHTTPServer(HTTPServer):
    def __init__(self, awaited_event_queue: Queue, event_queue: Queue):
        super().__init__(('localhost', 8080), PostHTTPRequestHandler)
        self.awaited_event_queue = awaited_event_queue
        self.event_queue = event_queue
