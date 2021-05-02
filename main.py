import datetime
from datetime import timedelta
from queue import Queue

from event import Event, TimedEvent
from event_scheduler import EventScheduler
from iva import Iva
from iva_communicator import IvaCommunicator


def main():
    event_queue = Queue()

    event_scheduler = EventScheduler(event_queue)
    event_scheduler.start()

    iva_communicator = IvaCommunicator('localhost', 5678)
    iva_communicator.start()

    iva = Iva(event_queue, iva_communicator)
    iva.start()

    event_scheduler.add_timed_event(TimedEvent(Event('MORNING'), datetime.datetime.now() + timedelta(seconds=3)))
    event_scheduler.add_timed_event(TimedEvent(Event('MORNING_CALLBACK'), datetime.datetime.now() + timedelta(seconds=10)))


main()
