from datetime import datetime
from threading import Thread

from event_scheduler import EventScheduler
from events.events import UtteranceIntentEvent, RaspberryEvent
from raspberry_client.client import RaspberryClient


class UtteranceIntentEventHandler(Thread):
    def __init__(self, event: UtteranceIntentEvent, event_scheduler: EventScheduler):
        super().__init__()
        self.event = event
        self.event_scheduler = event_scheduler
        self.intent_dispatcher = {
            UtteranceIntentEvent.Intent.TURN_SCREEN_ON: self.__handle_turn_screen_on_intent,
            UtteranceIntentEvent.Intent.TURN_SCREEN_OFF: self.__handle_turn_screen_off_intent,
            UtteranceIntentEvent.Intent.INTRODUCE_YOURSELF: self.__handle_introduce_yourself_intent,
            UtteranceIntentEvent.Intent.TELL_TIME: self.__handle_tell_time_intent,
            UtteranceIntentEvent.Intent.SPOTIFY_PLAY: self.__handle_spotify_play_intent,
            UtteranceIntentEvent.Intent.SPOTIFY_STOP: self.__handle_spotify_stop_intent,
        }

    def run(self):
        print(f'Handling {self.event}')
        try:
            self.intent_dispatcher[self.event.intent]()
        except KeyError:
            print(f'Handler for {self.event.intent} is not implemented')

    def __handle_introduce_yourself_intent(self):
        if self.event.output_provider:
            self.event.output_provider.output('I am IVA.')

    def __handle_tell_time_intent(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        if self.event.output_provider:
            self.event.output_provider.output(f'The time is {current_time}')

    def __handle_turn_screen_on_intent(self):
        self.event_scheduler.schedule_event(RaspberryEvent(RaspberryClient.Action.SCREEN_ON))

    def __handle_turn_screen_off_intent(self):
        self.event_scheduler.schedule_event(RaspberryEvent(RaspberryClient.Action.SCREEN_OFF))

    def __handle_spotify_play_intent(self):
        print('Spotify play intent')

    def __handle_spotify_stop_intent(self):
        print('Spotify stop intent')
