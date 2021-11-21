from __future__ import annotations

from queue import Queue
from threading import Thread
from events.events import CommandEvent, ChooseMealEvent, StartRoutineEvent, RoutineType, RaspberryEvent, \
    RefreshFrontendComponentEvent, SpotifyEvent
from raspberry_client.client import RaspberryClient


class CommandEventHandler(Thread):
    """
    Handles pre-defined user commands
    """

    def __init__(self, event_queue: Queue, iva: Iva):
        super().__init__()
        self.event_queue = event_queue
        self.iva = iva
        self.command_dispatcher = {
            'start_routine': self.__handle_start_routine_command,
            'turn_screen_on': self.__handle_turn_screen_on_command,
            'turn_screen_off': self.__handle_turn_screen_off_command,
            'choose_meal': self.__handle_choose_meal_command,
            'refresh_component': self.__handle_refresh_component_command,
            'say': self.__handle_say_command,
            'toggle_intent_confirmation': self.__toggle_ask_user_to_confirm_intent_prediction_config_flag,
            'spotify_play': self.__handle_spotify_play,
            'spotify_stop': self.__handle_spotify_stop,
        }

    def run(self):
        while True:
            event: CommandEvent = self.event_queue.get()
            print(f'Handling {event}')
            try:
                self.command_dispatcher[event.command](event)
            except KeyError:
                print(f'Undefined command: "{event.command}"')

    def __handle_start_routine_command(self, event: CommandEvent):
        # TODO: handle a missing parameter
        routine_type = RoutineType(event.args[0])
        self.iva.event_scheduler.schedule_event(StartRoutineEvent(routine_type))

    def __handle_turn_screen_on_command(self, _event: CommandEvent):
        self.iva.event_scheduler.schedule_event(RaspberryEvent(RaspberryClient.Action.SCREEN_ON))

    def __handle_turn_screen_off_command(self, _event: CommandEvent):
        self.iva.event_scheduler.schedule_event(RaspberryEvent(RaspberryClient.Action.SCREEN_OFF))

    def __handle_choose_meal_command(self, _event: CommandEvent):
        self.iva.event_scheduler.schedule_event(ChooseMealEvent())

    def __handle_refresh_component_command(self, event: CommandEvent):
        # TODO: handle a missing parameter
        component = RefreshFrontendComponentEvent.Component(event.args[0])
        self.iva.event_scheduler.schedule_event(RefreshFrontendComponentEvent(component))

    def __handle_say_command(self, event: CommandEvent):
        text_to_say = ' '.join(event.args)
        self.iva.tts_client.output(text_to_say)

    def __toggle_ask_user_to_confirm_intent_prediction_config_flag(self, _event: CommandEvent):
        self.iva.config.ask_user_to_confirm_intent_prediction = not self.iva.config.ask_user_to_confirm_intent_prediction

    def __handle_spotify_play(self, _event: CommandEvent):
        self.iva.event_scheduler.schedule_event(SpotifyEvent(SpotifyEvent.Action.PLAY))

    def __handle_spotify_stop(self, _event: CommandEvent):
        self.iva.event_scheduler.schedule_event(SpotifyEvent(SpotifyEvent.Action.STOP))
