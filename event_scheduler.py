from queue import Queue
from threading import Thread, RLock
from datetime import datetime
from event import Event, TimedEvent
from sortedcontainers import SortedList


class EventScheduler(Thread):
    def __init__(self, event_queue: Queue):
        super().__init__()
        self.event_queue = event_queue
        self.timed_events = SortedList()
        self.lock = RLock()

    def schedule_event(self, event: Event, event_time: datetime = None):
        if event_time:
            self.add_timed_event(TimedEvent(event, event_time))
        else:
            self.event_queue.put(event)

    def add_timed_event(self, timed_event: TimedEvent):
        with self.lock:
            self.timed_events.add(timed_event)

    def run(self):
        while True:
            with self.lock:
                current_time = datetime.now()
                while len(self.timed_events) > 0 and self.timed_events[0].event_time < current_time:
                    timed_event = self.timed_events.pop(0)
                    self.event_queue.put(timed_event.event)
