import datetime
import threading
from datetime import timedelta
from queue import Queue

from event_scheduler import EventScheduler
from events.events import StartMorningRoutineEvent
from events.timed_events import DailyTimedEvent
from frontend.frontend_socket_server import FrontendSocketServer
from http_server.http_server import SimpleHTTPServer
from iva import Iva


def main():
    event_queue = Queue()
    awaited_event_queue = Queue()

    event_scheduler = EventScheduler(event_queue)
    event_scheduler.start()

    frontend_socket_server = FrontendSocketServer('localhost', 5678)
    frontend_socket_server.start()

    iva = Iva(event_queue, awaited_event_queue, frontend_socket_server)
    iva.start()

    event_scheduler.add_timed_event(DailyTimedEvent(StartMorningRoutineEvent(), datetime.datetime.now() + timedelta(seconds=5)))

    server = SimpleHTTPServer(awaited_event_queue, event_queue)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()


main()
