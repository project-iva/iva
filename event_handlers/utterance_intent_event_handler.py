from datetime import datetime
from queue import Queue
from threading import Thread

from event_scheduler import EventScheduler
from events.events import UtteranceIntentEvent, RaspberryEvent, SpotifyEvent, StartRoutineEvent
from intent_helpers.jokes_api_wrapper import JokesAPIWrapper
from raspberry_client.client import RaspberryClient


class UtteranceIntentEventHandler(Thread):
    """
    Executes action based on the utterance intent
    """

    def __init__(self, event_queue: Queue, event_scheduler: EventScheduler):
        super().__init__()
        self.event_queue = event_queue
        self.event_scheduler = event_scheduler
        self.intent_dispatcher = {
            UtteranceIntentEvent.Intent.TURN_SCREEN_ON: self.__handle_turn_screen_on_intent,
            UtteranceIntentEvent.Intent.TURN_SCREEN_OFF: self.__handle_turn_screen_off_intent,
            UtteranceIntentEvent.Intent.INTRODUCE_YOURSELF: self.__handle_introduce_yourself_intent,
            UtteranceIntentEvent.Intent.TELL_TIME: self.__handle_tell_time_intent,
            UtteranceIntentEvent.Intent.SPOTIFY_PLAY: self.__handle_spotify_play_intent,
            UtteranceIntentEvent.Intent.SPOTIFY_STOP: self.__handle_spotify_stop_intent,
            UtteranceIntentEvent.Intent.TELL_JOKE: self.__handle_tell_joke_intent,
            UtteranceIntentEvent.Intent.START_MORNING_ROUTINE: self.__handle_start_morning_routine,
            UtteranceIntentEvent.Intent.START_EVENING_ROUTINE: self.__handle_start_evening_routine,
        }

    def run(self):
        while True:
            event: UtteranceIntentEvent = self.event_queue.get()
            print(f'Handling {event}')
            try:
                self.intent_dispatcher[event.intent](event)
            except KeyError:
                print(f'Handler for {event.intent} is not implemented')

    def __handle_introduce_yourself_intent(self, event: UtteranceIntentEvent):
        if event.output_provider:
            event.output_provider.output('I am IVA.')

    def __handle_tell_time_intent(self, event: UtteranceIntentEvent):
        current_time = datetime.now().strftime("%H:%M:%S")
        if event.output_provider:
            event.output_provider.output(f'The time is {current_time}')

    def __handle_turn_screen_on_intent(self, _event: UtteranceIntentEvent):
        self.event_scheduler.schedule_event(RaspberryEvent(RaspberryClient.Action.SCREEN_ON))

    def __handle_turn_screen_off_intent(self, _event: UtteranceIntentEvent):
        self.event_scheduler.schedule_event(RaspberryEvent(RaspberryClient.Action.SCREEN_OFF))

    def __handle_spotify_play_intent(self, _event: UtteranceIntentEvent):
        self.event_scheduler.schedule_event(SpotifyEvent(SpotifyEvent.Action.PLAY))

    def __handle_spotify_stop_intent(self, _event: UtteranceIntentEvent):
        self.event_scheduler.schedule_event(SpotifyEvent(SpotifyEvent.Action.STOP))

    def __handle_tell_joke_intent(self, event: UtteranceIntentEvent):
        if event.output_provider:
            joke = JokesAPIWrapper.fetch_joke()
            # remove new line symbols in the text
            joke_text = joke.joke.replace('\n', '')
            event.output_provider.output(joke_text)

    def __handle_start_morning_routine(self, _event: UtteranceIntentEvent):
        self.event_scheduler.schedule_event(StartRoutineEvent(StartRoutineEvent.Type.MORNING))

    def __handle_start_evening_routine(self, _event: UtteranceIntentEvent):
        self.event_scheduler.schedule_event(StartRoutineEvent(StartRoutineEvent.Type.EVENING))
