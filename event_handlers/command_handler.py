from threading import Thread

from event_scheduler import EventScheduler
from events.events import CommandEvent, TurnRaspberryScreenOnEvent, \
    TurnRaspberryScreenOffEvent, ChooseMealEvent, StartRoutineEvent, RoutineType


class CommandHandler(Thread):
    def __init__(self, command_event: CommandEvent, event_scheduler: EventScheduler):
        super().__init__()
        self.command_event = command_event
        self.event_scheduler = event_scheduler
        self.command_dispatcher = {
            'start_routine': self.__handle_start_routine_command,
            'turn_screen_on': self.__handle_turn_screen_on_command,
            'turn_screen_off': self.__handle_turn_screen_off_command,
            'choose_meal': self.__handle_choose_meal_command
        }

    def run(self):
        print(f'Handling {self.command_event}')
        try:
            self.command_dispatcher[self.command_event.command]()
        except KeyError:
            print(f'Undefined command: "{self.command_event.command}"')

    def __handle_start_routine_command(self):
        # handle a missing parameter
        routine_type = RoutineType(self.command_event.args[0])
        self.event_scheduler.schedule_event(StartRoutineEvent(routine_type))

    def __handle_turn_screen_on_command(self):
        self.event_scheduler.schedule_event(TurnRaspberryScreenOnEvent())

    def __handle_turn_screen_off_command(self):
        self.event_scheduler.schedule_event(TurnRaspberryScreenOffEvent())

    def __handle_choose_meal_command(self):
        self.event_scheduler.schedule_event(ChooseMealEvent())
