from threading import Thread
from slack import RTMClient, WebClient

from events.events import CommandEvent, UtteranceEvent
from event_scheduler import EventScheduler


class SlackClientHandler(Thread):
    def __init__(self, slack_client_token: str, event_scheduler: EventScheduler):
        super().__init__()
        self.event_scheduler = event_scheduler
        self.rtm_client = RTMClient(token=slack_client_token)
        self.slack_web_client = WebClient(token=slack_client_token)
        self.rtm_client.on(event='message', callback=self.__handle_slack_message_event)

    def run(self):
        self.rtm_client.start()

    def send_message(self, text: str):
        self.slack_web_client.chat_postMessage(
            channel='#iva',
            text=text)

    def __handle_slack_message_event(self, **payload):
        data = payload['data']
        web_client = payload['web_client']
        text = data['text']

        # if the text starts with # then it should be a predefined command
        if text.startswith('#'):
            # strip the # from the command
            command_text = text[1:]
            command_and_args = command_text.split()
            args = command_and_args[1:]
            self.event_scheduler.schedule_event(CommandEvent(command=command_and_args[0], args=args))
        else:
            self.event_scheduler.schedule_event(UtteranceEvent(utterance=text))
