from threading import Thread

from event_scheduler import EventScheduler
from events.events import DayPlanActivityEvent, StartRoutineEvent, RoutineType, ChooseMealEvent
from models.day_plan import DayPlanActivityType


class DayPlanActivityEventHandler(Thread):
    def __init__(self, day_plan_activity_event: DayPlanActivityEvent, event_scheduler: EventScheduler):
        super().__init__()
        self.day_plan_activity_event = day_plan_activity_event
        self.event_scheduler = event_scheduler
        self.dispatcher = {
            DayPlanActivityType.MORNING_ROUTINE: self.__handle_morning_routine_activity,
            DayPlanActivityType.EVENING_ROUTINE: self.__handle_evening_routine_activity,
            DayPlanActivityType.MEAL: self.__handle_meal_activity,
        }

    def run(self):
        print(f'Handling {self.day_plan_activity_event}')
        if dispatch := self.dispatcher.get(self.day_plan_activity_event.activity.type):
            dispatch()

    def __handle_morning_routine_activity(self):
        self.event_scheduler.schedule_event(StartRoutineEvent(RoutineType.MORNING))

    def __handle_evening_routine_activity(self):
        self.event_scheduler.schedule_event(StartRoutineEvent(RoutineType.EVENING))

    def __handle_meal_activity(self):
        self.event_scheduler.schedule_event(ChooseMealEvent())
