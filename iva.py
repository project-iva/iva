import uuid
from queue import Queue
from threading import Thread
from typing import Dict
from uuid import UUID

from control_session.session import PresenterControlSession
from event_handlers.backend_data_updated_event_handler import BackendDataUpdatedEventHandler
from event_handlers.choose_meal_event_handler import ChooseMealEventHandler
from event_handlers.command_event_handler import CommandEventHandler
from event_handlers.day_plan_activity_event_handler import DayPlanActivityEventHandler
from event_handlers.raspberry_event_handler import RaspberryEventHandler
from event_handlers.refresh_day_data_event_handler import RefreshDayDataEventHandler
from event_handlers.refresh_frontend_component_event_handler import RefreshFrontendComponentEventHandler
from event_handlers.schedule_day_plan_event_handler import ScheduleDayPlanEventHandler
from event_handlers.start_routine_event_handler import StartRoutineEventHandler
from event_handlers.utterance_event_handler import UtteranceEventHandler
from event_scheduler import EventScheduler
from events.events import StartRoutineEvent, CommandEvent, \
    UtteranceEvent, RaspberryEvent, ChooseMealEvent, \
    ScheduleDayPlanEvent, DayPlanActivityEvent, BackendDataUpdatedEvent, RefreshFrontendComponentEvent, \
    RefreshDayDataEvent
from intent_classifier.classifier import IntentClassifier
from slack_client.handler import SlackClientHandler
from websocket.server import WebSocketServer


class Iva(Thread):
    def __init__(self, event_queue: Queue, event_scheduler: EventScheduler,
                 socket_server: WebSocketServer, slack_client: SlackClientHandler, intent_classifier: IntentClassifier):
        super().__init__()
        self.event_queue = event_queue
        self.event_scheduler = event_scheduler
        self.socket_server = socket_server
        self.slack_client = slack_client
        self.control_sessions: Dict[UUID, PresenterControlSession] = {}
        self.intent_classifier = intent_classifier

        self.dispatcher = {
            StartRoutineEvent: self.__handle_start_routine_event,
            CommandEvent: self.__handle_command_event,
            UtteranceEvent: self.__handle_utterance_event,
            RaspberryEvent: self.__handle_raspberry_event,
            ChooseMealEvent: self.__handle_choose_meal_event,
            ScheduleDayPlanEvent: self.__handle_schedule_day_plan_event,
            DayPlanActivityEvent: self.__handle_day_plan_activity_event,
            BackendDataUpdatedEvent: self.__handle_backend_data_updated_event,
            RefreshFrontendComponentEvent: self.__handle_refresh_frontend_component_event,
            RefreshDayDataEvent: self.__handle_refresh_day_data_event,
        }

    def register_control_session(self, control_session: PresenterControlSession) -> uuid:
        session_uuid = uuid.uuid4()
        self.control_sessions[session_uuid] = control_session
        return session_uuid

    def unregister_control_session(self, session_uuid: uuid):
        try:
            self.control_sessions.pop(session_uuid)
        except KeyError:
            pass

    def refresh_day_plan(self):
        self.__handle_schedule_day_plan_event(ScheduleDayPlanEvent())

    def run(self):
        while True:
            event = self.event_queue.get()
            self.dispatcher[type(event)](event)
            self.event_queue.task_done()

    def __handle_start_routine_event(self, start_routine_event: StartRoutineEvent):
        handler = StartRoutineEventHandler(start_routine_event, self)
        handler.start()

    def __handle_command_event(self, command_event: CommandEvent):
        handler = CommandEventHandler(command_event, self.event_scheduler)
        handler.start()

    def __handle_utterance_event(self, utterance_event: UtteranceEvent):
        handler = UtteranceEventHandler(utterance_event, self.slack_client, self.intent_classifier,
                                        self.event_scheduler)
        handler.start()

    def __handle_raspberry_event(self, raspberry_event: RaspberryEvent):
        handler = RaspberryEventHandler(raspberry_event)
        handler.start()

    def __handle_choose_meal_event(self, choose_meal_event: ChooseMealEvent):
        handler = ChooseMealEventHandler(choose_meal_event, self)
        handler.start()

    def __handle_schedule_day_plan_event(self, schedule_day_plan_event: ScheduleDayPlanEvent):
        handler = ScheduleDayPlanEventHandler(schedule_day_plan_event, self.event_scheduler)
        handler.start()

    def __handle_day_plan_activity_event(self, day_plan_activity_event: DayPlanActivityEvent):
        handler = DayPlanActivityEventHandler(day_plan_activity_event, self.event_scheduler)
        handler.start()

    def __handle_backend_data_updated_event(self, data_updated_event: BackendDataUpdatedEvent):
        handler = BackendDataUpdatedEventHandler(data_updated_event, self)
        handler.start()

    def __handle_refresh_frontend_component_event(self,
                                                  refresh_frontend_component_event: RefreshFrontendComponentEvent):
        handler = RefreshFrontendComponentEventHandler(refresh_frontend_component_event, self)
        handler.start()

    def __handle_refresh_day_data_event(self, event: RefreshDayDataEvent):
        handler = RefreshDayDataEventHandler(event, self.event_scheduler)
        handler.start()
