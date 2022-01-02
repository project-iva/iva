import uuid
from queue import Queue
from threading import Thread
from typing import Dict, Optional
from uuid import UUID

from control_session.session import PresenterControlSession
from event_handlers import *
from event_handlers.config_command_event_handler import ConfigCommandEventHandler
from event_scheduler import EventScheduler
from events.events import StartRoutineEvent, CommandEvent, \
    UtteranceEvent, RaspberryEvent, ChooseMealEvent, \
    ScheduleDayPlanEvent, DayPlanActivityEvent, BackendDataUpdatedEvent, RefreshFrontendComponentEvent, \
    RefreshDayDataEvent, UtteranceIntentEvent, SpotifyEvent, ConfigCommandEvent
from intent_classifier.classifier import IntentClassifier
from interactions.input_provider import InputProvider
from interactions.output_provider import OutputProvider
from iva_config import IvaConfig
from slack_client.handler import SlackClientHandler
from intent_helpers.spotify_client_wrapper import SpotifyClientWrapper
from tts_client.tts_client import TextToSpeechClient
from websocket.server import WebSocketServer


class Iva(Thread):
    def __init__(self, event_queue: Queue, event_scheduler: EventScheduler, socket_server: WebSocketServer,
                 slack_client: SlackClientHandler, intent_classifier: IntentClassifier,
                 spotify_client: SpotifyClientWrapper):
        super().__init__()
        self.event_queue = event_queue
        self.event_scheduler = event_scheduler
        self.socket_server = socket_server
        self.slack_client = slack_client
        self.control_sessions: Dict[UUID, PresenterControlSession] = {}
        self.intent_classifier = intent_classifier
        self.tts_client = TextToSpeechClient(self.event_scheduler)
        self.config = IvaConfig(ask_user_to_confirm_intent_prediction_for_confidence_lower_than=0.95)
        self.spotify_client = spotify_client

        # event handlers queues
        self.backend_data_updated_event_queue = Queue()
        self.choose_meal_event_queue = Queue()
        self.command_event_queue = Queue()
        self.day_plan_activity_event_queue = Queue()
        self.raspberry_event_queue = Queue()
        self.refresh_day_data_event_queue = Queue()
        self.refresh_frontend_component_event_queue = Queue()
        self.schedule_day_plan_event_queue = Queue()
        self.spotify_event_queue = Queue()
        self.start_routine_event_queue = Queue()
        self.utterance_event_queue = Queue()
        self.utterance_intent_event_queue = Queue()
        self.config_command_event_queue = Queue()

        self.queue_dispatcher = {
            StartRoutineEvent: self.start_routine_event_queue,
            CommandEvent: self.command_event_queue,
            UtteranceEvent: self.utterance_event_queue,
            RaspberryEvent: self.raspberry_event_queue,
            ChooseMealEvent: self.choose_meal_event_queue,
            ScheduleDayPlanEvent: self.schedule_day_plan_event_queue,
            DayPlanActivityEvent: self.day_plan_activity_event_queue,
            BackendDataUpdatedEvent: self.backend_data_updated_event_queue,
            RefreshFrontendComponentEvent: self.refresh_frontend_component_event_queue,
            RefreshDayDataEvent: self.refresh_day_data_event_queue,
            UtteranceIntentEvent: self.utterance_intent_event_queue,
            SpotifyEvent: self.spotify_event_queue,
            ConfigCommandEvent: self.config_command_event_queue,
        }
        self.__start_handlers()

    def __start_handlers(self):
        BackendDataUpdatedEventHandler(self.backend_data_updated_event_queue, self.event_scheduler).start()
        ChooseMealEventHandler(self.choose_meal_event_queue, self).start()
        CommandEventHandler(self.command_event_queue, self).start()
        DayPlanActivityEventHandler(self.day_plan_activity_event_queue, self.event_scheduler).start()
        RaspberryEventHandler(self.raspberry_event_queue).start()
        RefreshDayDataEventHandler(self.refresh_day_data_event_queue, self.event_scheduler).start()
        RefreshFrontendComponentEventHandler(self.refresh_frontend_component_event_queue, self.socket_server).start()
        ScheduleDayPlanEventHandler(self.schedule_day_plan_event_queue, self.event_scheduler).start()
        SpotifyEventHandler(self.spotify_event_queue, self.spotify_client).start()
        StartRoutineEventHandler(self.start_routine_event_queue, self).start()
        UtteranceEventHandler(self.utterance_event_queue, self.intent_classifier, self).start()
        UtteranceIntentEventHandler(self.utterance_intent_event_queue, self.event_scheduler).start()
        ConfigCommandEventHandler(self.config_command_event_queue).start()

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

    def handle_utterance(self, utterance: str, input_provider: Optional[InputProvider] = None,
                         output_provider: Optional[OutputProvider] = None):
        if not output_provider:
            # use TTS as default output provider
            output_provider = self.tts_client

        self.event_scheduler.schedule_event(
            UtteranceEvent(utterance=utterance, input_provider=input_provider, output_provider=output_provider)
        )

    def run(self):
        while True:
            event = self.event_queue.get()
            try:
                queue = self.queue_dispatcher[type(event)]
            except KeyError:
                print(f'Handler for {event} not implemented!')
            else:
                queue.put(event)
