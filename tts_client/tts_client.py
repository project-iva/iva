from event_scheduler import EventScheduler
from events.events import RaspberryEvent
from interactions.output_provider import OutputProvider
from raspberry_client.client import RaspberryClient


class TextToSpeechClient(OutputProvider):
    def __init__(self, event_scheduler: EventScheduler):
        self.event_scheduler = event_scheduler

    def output(self, output: str):
        extra_data = {
            'tts_data': output
        }
        self.event_scheduler.schedule_event(RaspberryEvent(RaspberryClient.Action.SAY, extra_data))
