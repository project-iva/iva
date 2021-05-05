import datetime
import uuid
from datetime import timedelta
from queue import Queue

from event_scheduler import EventScheduler
from events.events import StartMorningRoutineEvent, AwaitedEvent
from events.timed_events import TimedEvent, DailyTimedEvent
from frontend.frontend_socket_server import FrontendSocketServer
from iva import Iva


def main():
    event_queue = Queue()

    event_scheduler = EventScheduler(event_queue)
    event_scheduler.start()

    frontend_socket_server = FrontendSocketServer('localhost', 5678)
    frontend_socket_server.start()

    iva = Iva(event_queue, frontend_socket_server)
    iva.start()

    event_scheduler.add_timed_event(DailyTimedEvent(StartMorningRoutineEvent(), datetime.datetime.now() + timedelta(seconds=3)))
    event_scheduler.add_timed_event(TimedEvent(AwaitedEvent(uuid.UUID('e102589b-36b3-4624-86cb-51180cf3865c')), datetime.datetime.now() + timedelta(seconds=10)))


main()
