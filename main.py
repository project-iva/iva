import datetime
import os
import threading
from queue import Queue
from dotenv import load_dotenv
from event_scheduler import EventScheduler
from events.events import ScheduleDayPlanEvent, RefreshDayDataEvent
from events.timed_events import DailyTimedEvent
from http_server.server import app as flask_app
from intent_classifier.classifier import IntentClassifier
from iva import Iva
from slack_client.handler import SlackClientHandler
from intent_helpers.spotify_client_wrapper import SpotifyClientWrapper
from websocket.server import WebSocketServer


def main():
    print('Starting IVA...')
    load_dotenv()

    event_queue = Queue()

    event_scheduler = EventScheduler(event_queue)
    event_scheduler.start()

    intent_classifier = IntentClassifier()
    intent_classifier.start()

    frontend_socket_server = WebSocketServer('0.0.0.0', 5678)
    frontend_socket_server.start()

    slack_client_token = os.environ.get('SLACK_CLIENT_TOKEN')
    slack_client = SlackClientHandler(slack_client_token, event_scheduler)
    slack_client.start()

    spotify_client = SpotifyClientWrapper()

    iva = Iva(event_queue, event_scheduler, frontend_socket_server, slack_client, intent_classifier, spotify_client)
    iva.start()

    event_scheduler.schedule_event(ScheduleDayPlanEvent())

    # start automatic refreshing of data and views at 2 AM
    event_scheduler.schedule_timed_event(
        DailyTimedEvent(RefreshDayDataEvent(),
                        datetime.datetime.now().replace(hour=2, minute=0) + datetime.timedelta(days=1))
    )

    flask_app.iva = iva
    threading.Thread(target=flask_app.run, kwargs={'host': '0.0.0.0', 'debug': True, 'use_reloader': False}).start()


main()
