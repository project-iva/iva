from __future__ import annotations

from queue import Queue
from threading import Thread
from events.events import BackendDataUpdatedEvent, RefreshFrontendComponentEvent


class BackendDataUpdatedEventHandler(Thread):
    def __init__(self, event_queue: Queue, iva: Iva):
        super().__init__()
        self.event_queue = event_queue
        self.iva = iva
        self.dispatcher = {
            BackendDataUpdatedEvent.DataType.CALORIES: self.__handle_calories_data_updated,
            BackendDataUpdatedEvent.DataType.BODY_MASS: self.__handle_body_mass_data_updated,
            BackendDataUpdatedEvent.DataType.DAY_PLAN: self.__handle_day_plan_data_updated,
            BackendDataUpdatedEvent.DataType.DAY_GOALS: self.__handle_day_goals_data_updated,
            BackendDataUpdatedEvent.DataType.SLEEP: self.__handle_sleep_data_updated,
            BackendDataUpdatedEvent.DataType.MINDFUL_SESSIONS: self.__handle_mindful_sessions_data_updated,
        }

    def run(self):
        while True:
            event: BackendDataUpdatedEvent = self.event_queue.get()
            print(f'Handling {event}')
            self.dispatcher[event.data_type]()

    def __handle_calories_data_updated(self):
        self.iva.event_scheduler.schedule_event(
            RefreshFrontendComponentEvent(RefreshFrontendComponentEvent.Component.CALORIES_VIEW))

    def __handle_body_mass_data_updated(self):
        self.iva.event_scheduler.schedule_event(
            RefreshFrontendComponentEvent(RefreshFrontendComponentEvent.Component.BODY_MASS_VIEW))

    def __handle_day_plan_data_updated(self):
        self.iva.event_scheduler.schedule_event(
            RefreshFrontendComponentEvent(RefreshFrontendComponentEvent.Component.DAY_PLAN_VIEW))
        self.iva.refresh_day_plan()

    def __handle_day_goals_data_updated(self):
        self.iva.event_scheduler.schedule_event(
            RefreshFrontendComponentEvent(RefreshFrontendComponentEvent.Component.DAY_GOALS_VIEW))

    def __handle_sleep_data_updated(self):
        self.iva.event_scheduler.schedule_event(
            RefreshFrontendComponentEvent(RefreshFrontendComponentEvent.Component.SLEEP_STATS_VIEW))

    def __handle_mindful_sessions_data_updated(self):
        self.iva.event_scheduler.schedule_event(
            RefreshFrontendComponentEvent(RefreshFrontendComponentEvent.Component.MINDFUL_SESSIONS_STATS_VIEW))
