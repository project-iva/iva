from threading import Thread

from event_scheduler import EventScheduler
from events.events import CommandEvent, ChooseMealEvent, StartRoutineEvent, RoutineType, RaspberryEvent, \
    RefreshFrontendComponentEvent
from raspberry_client.client import RaspberryClient
from tts_client.tts_client import TextToSpeechClient


class CommandEventHandler(Thread):
    def __init__(self, command_event: CommandEvent, event_scheduler: EventScheduler, tts_client: TextToSpeechClient):
        super().__init__()
        self.command_event = command_event
        self.event_scheduler = event_scheduler
        self.tts_client = tts_client
        self.command_dispatcher = {
            'start_routine': self.__handle_start_routine_command,
            'turn_screen_on': self.__handle_turn_screen_on_command,
            'turn_screen_off': self.__handle_turn_screen_off_command,
            'choose_meal': self.__handle_choose_meal_command,
            'refresh_component': self.__handle_refresh_component_command,
            'say': self.__handle_say_command
        }

    def run(self):
        print(f'Handling {self.command_event}')
        try:
            self.command_dispatcher[self.command_event.command]()
        except KeyError:
            print(f'Undefined command: "{self.command_event.command}"')

    def __handle_start_routine_command(self):
        # TODO: handle a missing parameter
        routine_type = RoutineType(self.command_event.args[0])
        self.event_scheduler.schedule_event(StartRoutineEvent(routine_type))

    def __handle_turn_screen_on_command(self):
        self.event_scheduler.schedule_event(RaspberryEvent(RaspberryClient.Action.SCREEN_ON))

    def __handle_turn_screen_off_command(self):
        self.event_scheduler.schedule_event(RaspberryEvent(RaspberryClient.Action.SCREEN_OFF))

    def __handle_choose_meal_command(self):
        self.event_scheduler.schedule_event(ChooseMealEvent())

    def __handle_refresh_component_command(self):
        # TODO: handle a missing parameter
        component = RefreshFrontendComponentEvent.Component(self.command_event.args[0])
        self.event_scheduler.schedule_event(RefreshFrontendComponentEvent(component))

    def __handle_say_command(self):
        text_to_say = ' '.join(self.command_event.args)
        self.tts_client.output(text_to_say)
