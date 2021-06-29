from collections import deque
from queue import Queue
from threading import Thread
from typing import Dict, Type
from uuid import UUID

from event_handlers.choose_meal_handler import ChooseMealHandler
from event_handlers.command_handler import CommandHandler
from event_handlers.evening_routine_handler import EveningRoutineEventHandler
from event_handlers.morning_routine_event_handler import MorningRoutineEventHandler
from event_handlers.raspberry_event_handler import RaspberryEventHandler
from event_scheduler import EventScheduler
from events.events import AwaitedEvent, StartMorningRoutineEvent, StartEveningRoutineEvent, Event, CommandEvent, \
    UtteranceEvent, RaspberryEvent, TurnRaspberryScreenOnEvent, TurnRaspberryScreenOffEvent, ChooseMealEvent
from websocket.server import WebSocketServer

# TODO: Queue seems like an overkill for an listener, maybe refactor to and threading.Event with extra data
EventUuidListener = Dict[UUID, Queue]
EventTypeListener = Dict[Type[Event], Queue]


class Iva(Thread):
    def __init__(self, event_queue: Queue, awaited_event_uuids: deque, event_scheduler: EventScheduler,
                 socket_server: WebSocketServer):
        super().__init__()
        self.event_queue = event_queue
        self.awaited_event_uuids = awaited_event_uuids
        self.event_scheduler = event_scheduler
        self.socket_server = socket_server
        self.event_uuid_listeners: EventUuidListener = {}
        self.event_type_listeners: EventTypeListener = {}
        self.dispatcher = {
            AwaitedEvent: self.__handle_awaited_event,
            StartMorningRoutineEvent: self.__handle_start_morning_routine_event,
            StartEveningRoutineEvent: self.__handle_start_evening_routine_event,
            CommandEvent: self.__handle_command_event,
            UtteranceEvent: self.__handle_utterance_event,
            TurnRaspberryScreenOnEvent: self.__handle_raspberry_event,
            TurnRaspberryScreenOffEvent: self.__handle_raspberry_event,
            ChooseMealEvent: self.__handle_choose_meal_event
        }

    def register_event_uuid_listener(self, uuid: UUID, queue: Queue):
        self.event_uuid_listeners[uuid] = queue
        self.awaited_event_uuids.append(uuid)

    def register_event_type_listener(self, event_type: Type[Event], queue: Queue):
        self.event_type_listeners[event_type] = queue

    def unregister_event_uuid_listener(self, uuid: UUID):
        self.event_uuid_listeners.pop(uuid, None)
        try:
            self.awaited_event_uuids.remove(uuid)
        except ValueError:
            pass

    def unregister_event_type_listener(self, event_type: Type[Event]):
        self.event_type_listeners.pop(event_type, None)

    def run(self):
        while True:
            event = self.event_queue.get()
            self.dispatcher[type(event)](event)
            self.event_queue.task_done()

    def __handle_awaited_event(self, awaited_event: AwaitedEvent):
        # first check if there is a listener for a specific uuid
        if listener := self.event_uuid_listeners.pop(awaited_event.event.uuid, None):
            print('passing event to an uuid listener')
            listener.put(awaited_event.event)
            return

        # otherwise check if there is a listener for the specific type
        if listener := self.event_type_listeners.pop(type(awaited_event.event), None):
            print('passing event to an uuid listener')
            listener.put(awaited_event.event)
            return

        # there is awaited event but no listeners
        print(f'There are no listeners for AwaitedEvent: {awaited_event}')

    def __handle_start_morning_routine_event(self, start_morning_routine_event: StartMorningRoutineEvent):
        handler = MorningRoutineEventHandler(start_morning_routine_event, self, self.socket_server)
        handler.start()

    def __handle_start_evening_routine_event(self, start_evening_routine_event: StartEveningRoutineEvent):
        handler = EveningRoutineEventHandler(start_evening_routine_event, self, self.socket_server)
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
        handler = ChooseMealHandler(choose_meal_event)
        handler.start()
