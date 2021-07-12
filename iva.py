import uuid
from queue import Queue
from threading import Thread
from typing import Dict
from uuid import UUID

from control_session.session import PresenterControlSession
from event_handlers.choose_meal_handler import ChooseMealHandler
from event_handlers.command_handler import CommandHandler
from event_handlers.raspberry_event_handler import RaspberryEventHandler
from event_handlers.start_routine_handler import StartRoutineEventHandler
from event_scheduler import EventScheduler
from events.events import StartRoutineEvent, CommandEvent, \
    UtteranceEvent, RaspberryEvent, TurnRaspberryScreenOnEvent, TurnRaspberryScreenOffEvent, ChooseMealEvent
from slack_client.handler import SlackClientHandler
from websocket.server import WebSocketServer


class Iva(Thread):
    def __init__(self, event_queue: Queue, event_scheduler: EventScheduler,
                 socket_server: WebSocketServer, slack_client: SlackClientHandler):
        super().__init__()
        self.event_queue = event_queue
        self.event_scheduler = event_scheduler
        self.socket_server = socket_server
        self.slack_client = slack_client
        self.control_sessions: Dict[UUID, PresenterControlSession] = {}

        self.dispatcher = {
            StartRoutineEvent: self.__handle_start_routine_event,
            CommandEvent: self.__handle_command_event,
            UtteranceEvent: self.__handle_utterance_event,
            TurnRaspberryScreenOnEvent: self.__handle_raspberry_event,
            TurnRaspberryScreenOffEvent: self.__handle_raspberry_event,
            ChooseMealEvent: self.__handle_choose_meal_event
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

    def run(self):
        while True:
            event = self.event_queue.get()
            self.dispatcher[type(event)](event)
            self.event_queue.task_done()

    def __handle_start_routine_event(self, start_routine_event: StartRoutineEvent):
        handler = StartRoutineEventHandler(start_routine_event, self)
        handler.start()

    def __handle_command_event(self, command_event: CommandEvent):
        handler = CommandHandler(command_event, self.event_scheduler)
        handler.start()

    def __handle_utterance_event(self, utterance_event: UtteranceEvent):
        pass

    def __handle_raspberry_event(self, raspberry_event: RaspberryEvent):
        handler = RaspberryEventHandler(raspberry_event, self.socket_server)
        handler.start()

    def __handle_choose_meal_event(self, choose_meal_event: ChooseMealEvent):
        handler = ChooseMealHandler(choose_meal_event, self)
        handler.start()
