from datetime import datetime
from threading import Thread

from event_scheduler import EventScheduler
from events.events import UtteranceIntentEvent, RaspberryEvent
from raspberry_client.client import RaspberryClient
from slack_client.handler import SlackClientHandler


class UtteranceIntentEventHandler(Thread):
    def __init__(self, event: UtteranceIntentEvent, event_scheduler: EventScheduler, slack_client: SlackClientHandler):
        super().__init__()
        self.event = event
        self.event_scheduler = event_scheduler
        self.slack_client = slack_client

    def run(self):
        print(f'Handling {self.event}')

    def handle_introduce_yourself_intent(self):
        self.slack_client.send_message('I am IVA.')

    def handle_tell_time_intent(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.slack_client.send_message(f'The time is {current_time}')

    def handle_turn_screen_on_intent(self):
        self.event_scheduler.schedule_event(RaspberryEvent(RaspberryClient.Action.SCREEN_ON))

    def handle_turn_screen_off_intent(self):
        self.event_scheduler.schedule_event(RaspberryEvent(RaspberryClient.Action.SCREEN_OFF))
