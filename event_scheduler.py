import time
from queue import Queue
from threading import Thread, RLock
from datetime import datetime, timedelta
from typing import List

from sortedcontainers import SortedList

from events.events import Event, DayPlanActivityEvent
from events.timed_events import TimedEvent, DailyTimedEvent


class EventScheduler(Thread):
    def __init__(self, event_queue: Queue):
        super().__init__()
        self.event_queue = event_queue
        self.timed_events = SortedList()
        self.timed_events_lock = RLock()
        self.day_plan_activity_events = SortedList()
        self.day_plan_activity_events_lock = RLock()

    def schedule_event(self, event: Event, event_time: datetime = None):
        if event_time:
            self.schedule_timed_event(TimedEvent(event, event_time))
        else:
            self.event_queue.put(event)

    def schedule_timed_event(self, timed_event: TimedEvent):
        with self.timed_events_lock:
            self.timed_events.add(timed_event)

    def clear_day_plan_activity_events(self):
        with self.day_plan_activity_events_lock:
            self.day_plan_activity_events.clear()

    def schedule_day_plan_activity_events(self, activity_events: List[DayPlanActivityEvent]):
        with self.day_plan_activity_events_lock:
            self.day_plan_activity_events.update(activity_events)

    def __check_and_queue_timed_events(self):
        with self.timed_events_lock:
            current_time = datetime.now()
            while len(self.timed_events) > 0 and self.timed_events[0].event_time < current_time:
                timed_event = self.timed_events.pop(0)
                if isinstance(timed_event, DailyTimedEvent):
                    # schedule the daily event for the next day again
                    timed_event.event_time = timed_event.event_time + timedelta(days=1)
                    # TODO: it may be better to create a copy of the event with an unique uuid
                    self.schedule_timed_event(timed_event)

                self.event_queue.put(timed_event.event)

    def __check_and_queue_day_plan_activity_events(self):
        with self.day_plan_activity_events_lock:
            current_time = datetime.now()
            while len(self.day_plan_activity_events) > 0 \
                    and self.day_plan_activity_events[0].activity.start_time < current_time:
                activity_event = self.day_plan_activity_events.pop(0)
                self.event_queue.put(activity_event)

    def run(self):
        while True:
            self.__check_and_queue_timed_events()
            self.__check_and_queue_day_plan_activity_events()
            time.sleep(0.5)
