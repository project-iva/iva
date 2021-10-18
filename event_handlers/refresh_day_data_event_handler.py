from threading import Thread

from event_scheduler import EventScheduler
from events.events import RefreshDayDataEvent, RefreshFrontendComponentEvent


class RefreshDayDataEventHandler(Thread):
    def __init__(self, event: RefreshDayDataEvent, event_scheduler: EventScheduler):
        super().__init__()
        self.event = event
        self.event_scheduler = event_scheduler

    def run(self):
        print(f'Handling {self.event}')
        # refresh calories view
        self.event_scheduler.schedule_event(
            RefreshFrontendComponentEvent(RefreshFrontendComponentEvent.Component.CALORIES_VIEW)
        )
        # refresh day goals view
        self.event_scheduler.schedule_event(
            RefreshFrontendComponentEvent(RefreshFrontendComponentEvent.Component.DAY_GOALS_VIEW)
        )
