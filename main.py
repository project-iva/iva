import datetime
from datetime import timedelta
from queue import Queue

from event import Event, TimedEvent
from event_scheduler import EventScheduler
from iva import Iva
from frontend.frontend_socket_server import FrontendSocketServer


def main():
    event_queue = Queue()

    event_scheduler = EventScheduler(event_queue)
    event_scheduler.start()

    frontend_socket_server = FrontendSocketServer('localhost', 5678)
    frontend_socket_server.start()

    iva = Iva(event_queue, frontend_socket_server)
    iva.start()

    event_scheduler.add_timed_event(TimedEvent(Event('MORNING'), datetime.datetime.now() + timedelta(seconds=3)))
    event_scheduler.add_timed_event(TimedEvent(Event('MORNING_CALLBACK'), datetime.datetime.now() + timedelta(seconds=10)))


main()
