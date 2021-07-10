from threading import Thread

from event_scheduler import EventScheduler
from events.events import CommandEvent, TurnRaspberryScreenOnEvent, \
    TurnRaspberryScreenOffEvent, ChooseMealEvent


class CommandHandler(Thread):
    def __init__(self, command_event: CommandEvent, event_scheduler: EventScheduler):
        super().__init__()
        self.command_event = command_event
        self.event_scheduler = event_scheduler
        self.command_dispatcher = {
            'start_morning_routine': self.__handle_start_morning_routine_command,
            'start_evening_routine': self.__handle_start_evening_routine_command,
            'turn_screen_on': self.__handle_turn_screen_on_command,
            'turn_screen_off': self.__handle_turn_screen_off_command,
            'choose_meal': self.__handle_choose_meal_command,
            'choice': self.__handle_choice_command,
        }

    def run(self):
        print(f'Handling {self.command_event}')
        try:
            self.command_dispatcher[self.command_event.command]()
        except KeyError:
            print(f'Undefined command: "{self.command_event.command}"')

    def __handle_start_morning_routine_command(self):
        self.event_scheduler.schedule_event(StartMorningRoutineEvent())

    def __handle_start_evening_routine_command(self):
        self.event_scheduler.schedule_event(StartEveningRoutineEvent())

    def __handle_turn_screen_on_command(self):
        self.event_scheduler.schedule_event(TurnRaspberryScreenOnEvent())

    def __handle_turn_screen_off_command(self):
        self.event_scheduler.schedule_event(TurnRaspberryScreenOffEvent())

    def __handle_choose_meal_command(self):
        self.event_scheduler.schedule_event(ChooseMealEvent())

    def __handle_choice_command(self):
        pass
        # choice_event = ChoiceEvent(choice=int(self.command_event.args[0]))
        # self.event_scheduler.schedule_awaited_event(AwaitedEvent(choice_event))
