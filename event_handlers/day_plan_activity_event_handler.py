from threading import Thread

from event_scheduler import EventScheduler
from events.events import DayPlanActivityEvent


class DayPlanActivityEventHandler(Thread):
    def __init__(self, day_plan_activity_event: DayPlanActivityEvent, event_scheduler: EventScheduler):
        super().__init__()
        self.day_plan_activity_event = day_plan_activity_event
        self.event_scheduler = event_scheduler

    def run(self):
        print(f'Handling {self.day_plan_activity_event}')
