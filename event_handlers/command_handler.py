from threading import Thread

from event_scheduler import EventScheduler
from events.events import CommandEvent, StartMorningRoutineEvent, StartEveningRoutineEvent


class CommandHandler(Thread):
    def __init__(self, command_event: CommandEvent, event_scheduler: EventScheduler):
        super().__init__()
        self.command_event = command_event
        self.event_scheduler = event_scheduler
        self.command_dispatcher = {
            'start_morning_routine': self.__handle_start_morning_routine_command,
            'start_evening_routine': self.__handle_start_evening_routine_command,
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
