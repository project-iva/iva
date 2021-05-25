from threading import Thread
from slack import RTMClient

from events.events import CommandEvent, UtteranceEvent
from iva import Iva


class SlackClientHandler(Thread):
    def __init__(self, slack_client_token: str, iva: Iva):
        super().__init__()
        self.iva = iva
        self.rtm_client = RTMClient(token=slack_client_token)
        self.rtm_client.on(event='message', callback=self.__handle_slack_message_event)

    def run(self):
        self.rtm_client.start()

    def __handle_slack_message_event(self, **payload):
        data = payload['data']
        web_client = payload['web_client']
        text = data['text']

        # if the text starts with # then it should be a predefined command
        if text.startswith('#'):
            # strip the # from the command
            self.iva.event_scheduler.schedule_event(CommandEvent(command=text[1:]))
        else:
            self.iva.event_scheduler.schedule_event(UtteranceEvent(utterance=text))
