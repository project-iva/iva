from threading import Thread
from slack import RTMClient, WebClient

from events.events import CommandEvent, UtteranceEvent
from event_scheduler import EventScheduler
from interactions.input_provider import InputProvider
from interactions.output_provider import OutputProvider
from slack_client.session import SlackSession


class UnableToCreateSlackSessionException(Exception):
    pass


class SlackClientHandler(Thread, InputProvider, OutputProvider):
    def __init__(self, slack_client_token: str, event_scheduler: EventScheduler):
        super().__init__()
        self.event_scheduler = event_scheduler
        self.rtm_client = RTMClient(token=slack_client_token)
        self.slack_web_client = WebClient(token=slack_client_token)
        self.rtm_client.on(event='message', callback=self.__handle_slack_message_event)
        self.active_session = None

    def run(self):
        self.rtm_client.start()

    def get_input(self) -> str:
        session = SlackSession()
        self.set_active_session(session)
        utterance = session.wait_for_an_utterance()
        self.close_active_session()
        return utterance

    def output(self, output: str):
        self.__send_message(output)

    def __send_message(self, text: str):
        self.slack_web_client.chat_postMessage(
            channel='#iva',
            text=text)

    def set_active_session(self, session: SlackSession):
        if self.active_session:
            raise UnableToCreateSlackSessionException

        self.active_session = session

    def close_active_session(self):
        self.active_session = None

    def __handle_slack_message_event(self, **payload):
        data = payload['data']
        # ignore bot messages
        if data.get('subtype') == 'bot_message':
            return
        text = data['text']

        # if the text starts with # then it should be a predefined command
        if text.startswith('#'):
            # strip the # from the command
            command_text = text[1:]
            command_and_args = command_text.split()
            args = command_and_args[1:]
            self.event_scheduler.schedule_event(CommandEvent(command=command_and_args[0], args=args))
        else:
            # if there is an active session expecting an utterance, forward it
            if self.active_session:
                self.active_session.add_new_utterance(text)
            else:
                # otherwise the utterance should be handled via an event
                self.event_scheduler.schedule_event(
                    UtteranceEvent(utterance=text, input_provider=self, output_provider=self)
                )
