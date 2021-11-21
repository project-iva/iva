from queue import Queue
from threading import Thread

from event_scheduler import EventScheduler
from events.events import RefreshDayDataEvent, RefreshFrontendComponentEvent


class RefreshDayDataEventHandler(Thread):
    """
    Refreshes all relevant components at the end of the day to make them ready for the following day
    """

    def __init__(self, event_queue: Queue, event_scheduler: EventScheduler):
        super().__init__()
        self.event_queue = event_queue
        self.event_scheduler = event_scheduler

    def run(self):
        while True:
            event: RefreshDayDataEvent = self.event_queue.get()
            print(f'Handling {event}')
            # refresh calories view
            self.event_scheduler.schedule_event(
                RefreshFrontendComponentEvent(RefreshFrontendComponentEvent.Component.CALORIES_VIEW)
            )
            # refresh day goals view
            self.event_scheduler.schedule_event(
                RefreshFrontendComponentEvent(RefreshFrontendComponentEvent.Component.DAY_GOALS_VIEW)
            )
            # refresh day plan view
            self.event_scheduler.schedule_event(
                RefreshFrontendComponentEvent(RefreshFrontendComponentEvent.Component.DAY_PLAN_VIEW)
            )
