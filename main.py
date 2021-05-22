import datetime
import threading
from datetime import timedelta
from queue import Queue

from event_scheduler import EventScheduler
from events.events import StartMorningRoutineEvent, StartEveningRoutineEvent
from events.timed_events import DailyTimedEvent
from websocket.server import WebSocketServer
from http_server.http_server import SimpleHTTPServer
from iva import Iva


def main():
    print('Starting IVA...')
    event_queue = Queue()
    awaited_event_queue = Queue()

    event_scheduler = EventScheduler(event_queue)
    event_scheduler.start()

    frontend_socket_server = WebSocketServer('0.0.0.0', 5678)
    frontend_socket_server.start()

    iva = Iva(event_queue, awaited_event_queue, frontend_socket_server)
    iva.start()

    event_scheduler.add_timed_event(DailyTimedEvent(StartEveningRoutineEvent(), datetime.datetime.now() + timedelta(seconds=5)))

    server = SimpleHTTPServer(awaited_event_queue, event_queue)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()


main()
