from queue import Queue
from threading import Thread

from event_scheduler import EventScheduler
from events.events import DayPlanActivityEvent, StartRoutineEvent, ChooseMealEvent
from models.day_plan import DayPlanActivityType


class DayPlanActivityEventHandler(Thread):
    """
    Responsible for firing up any follow up events after a specific day plan activity has started
    """

    def __init__(self, event_queue: Queue, event_scheduler: EventScheduler):
        super().__init__()
        self.event_queue = event_queue
        self.event_scheduler = event_scheduler
        self.activity_event_mapping = {
            DayPlanActivityType.MORNING_ROUTINE: StartRoutineEvent(StartRoutineEvent.Type.MORNING),
            DayPlanActivityType.EVENING_ROUTINE: StartRoutineEvent(StartRoutineEvent.Type.EVENING),
            DayPlanActivityType.MEAL: ChooseMealEvent(),
        }

    def run(self):
        while True:
            event: DayPlanActivityEvent = self.event_queue.get()
            print(f'Handling {event}')
            try:
                follow_up_event = self.activity_event_mapping[event.activity.type]
            except KeyError:
                pass
            else:
                self.event_scheduler.schedule_event(follow_up_event)
