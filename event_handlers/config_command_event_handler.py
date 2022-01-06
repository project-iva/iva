from dataclasses import asdict
from distutils.util import strtobool
from queue import Queue
from threading import Thread

from events.events import ConfigCommandEvent
from iva_config import IvaConfig


class ConfigCommandEventHandler(Thread):
    """
    Responsible for handling config commands
    """

    def __init__(self, event_queue: Queue, config: IvaConfig):
        super().__init__()
        self.event_queue = event_queue
        self.config = config
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

    def __handle_print_action(self, event: ConfigCommandEvent):
        config_dict = asdict(self.config)
        message = 'Config:\n'
        for key in config_dict.keys():
            message += f'{key}: {config_dict[key]}\n'

        event.output_provider.output(message)

    def __handle_set_action(self, event: ConfigCommandEvent):
        if len(event.args) != 2:
            event.output_provider.output('Invalid input format')
            return

        field_type = self.config.__annotations__.get(event.args[0])
        if not field_type:
            event.output_provider.output(f'"{event.args[0]}" is not a valid config setting')
            return

        #  convert common string representation to boolean
        if field_type == bool:
            field_type = lambda x: bool(strtobool(x))

        try:
            updated_value = field_type(event.args[1])
        except ValueError:
            event.output_provider.output(f'"{event.args[1]}" is not a valid value for this setting')
        else:
            setattr(self.config, event.args[0], updated_value)
