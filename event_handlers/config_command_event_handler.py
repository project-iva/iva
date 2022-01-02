from queue import Queue
from threading import Thread

from events.events import ConfigCommandEvent


class ConfigCommandEventHandler(Thread):
    """
    Responsible for handling config commands
    """

    def __init__(self, event_queue: Queue):
        super().__init__()
        self.event_queue = event_queue
        self.action_dispatcher = {
            ConfigCommandEvent.Action.PRINT: self.__handle_print_action,
            ConfigCommandEvent.Action.SET: self.__handle_set_action,
        }

    def run(self):
        while True:
            event: ConfigCommandEvent = self.event_queue.get()
            print(f'Handling {event}')
            try:
                self.action_dispatcher[event.action](event)
            except KeyError:
                print(f'Undefined action: {event.action}')

    def __handle_print_action(self, _event: ConfigCommandEvent):
        pass

    def __handle_set_action(self, event: ConfigCommandEvent):
        pass
