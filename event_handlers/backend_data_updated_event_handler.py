from queue import Queue
from threading import Thread

from event_scheduler import EventScheduler
from events.events import BackendDataUpdatedEvent, RefreshFrontendComponentEvent


class BackendDataUpdatedEventHandler(Thread):
    """
    Handles data updated events from the backend and signals frontend to refresh corresponding components
    """

    def __init__(self, event_queue: Queue, event_scheduler: EventScheduler):
        super().__init__()
        self.event_queue = event_queue
        self.event_scheduler = event_scheduler
        self.event_component_mapping = {
            BackendDataUpdatedEvent.DataType.CALORIES: RefreshFrontendComponentEvent.Component.CALORIES_VIEW,
            BackendDataUpdatedEvent.DataType.BODY_MASS: RefreshFrontendComponentEvent.Component.BODY_MASS_VIEW,
            BackendDataUpdatedEvent.DataType.DAY_PLAN: RefreshFrontendComponentEvent.Component.DAY_PLAN_VIEW,
            BackendDataUpdatedEvent.DataType.DAY_GOALS: RefreshFrontendComponentEvent.Component.DAY_GOALS_VIEW,
            BackendDataUpdatedEvent.DataType.SLEEP: RefreshFrontendComponentEvent.Component.SLEEP_STATS_VIEW,
            BackendDataUpdatedEvent.DataType.MINDFUL_SESSIONS: RefreshFrontendComponentEvent.Component.MINDFUL_SESSIONS_STATS_VIEW,
        }

    def run(self):
        while True:
            event: BackendDataUpdatedEvent = self.event_queue.get()
            print(f'Handling {event}')
            component = self.event_component_mapping[event.data_type]
            self.event_scheduler.schedule_event(RefreshFrontendComponentEvent(component))
