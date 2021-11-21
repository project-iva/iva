from queue import Queue
from threading import Thread
from datetime import datetime
from backend_client.client import BackendClient
from event_scheduler import EventScheduler
from events.events import ScheduleDayPlanEvent, DayPlanActivityEvent


class ScheduleDayPlanEventHandler(Thread):
    """
    Fetches day plan activities and creates timed events for them so that follow up events can be automatically triggered
    E.g. Morning routine activity, can automatically trigger an event which will start routine presenter in the frontend
    and create control session
    """

    def __init__(self, event_queue: Queue, event_scheduler: EventScheduler):
        super().__init__()
        self.event_queue = event_queue
        self.event_scheduler = event_scheduler

    def run(self):
        while True:
            event: ScheduleDayPlanEvent = self.event_queue.get()
            print(f'Handling {event}')
            current_day_plan = BackendClient.get_current_day_plan()
            current_time = datetime.now()
            # Filter for activities which has not started yet
            upcoming_activities = list(
                filter(lambda activity: activity.start_time > current_time, current_day_plan.activities)
            )
            activity_events = list(map(DayPlanActivityEvent, upcoming_activities))
            # Clear old day activity events
            self.event_scheduler.clear_day_plan_activity_events()
            # Schedule upcoming activities
            self.event_scheduler.schedule_day_plan_activity_events(activity_events)
