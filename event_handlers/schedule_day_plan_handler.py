from threading import Thread
from datetime import datetime
from backend_client.client import BackendClient
from event_scheduler import EventScheduler
from events.events import ScheduleDayPlanEvent, DayPlanActivityEvent


class ScheduleDayPlanHandler(Thread):
    def __init__(self, schedule_day_plan_event: ScheduleDayPlanEvent, event_scheduler: EventScheduler):
        super().__init__()
        self.schedule_day_plan_event = schedule_day_plan_event
        self.event_scheduler = event_scheduler

    def run(self):
        print(f'Handling {self.schedule_day_plan_event}')
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
