import os
import threading
from queue import Queue
from dotenv import load_dotenv
from event_scheduler import EventScheduler
from http_server.server import app as flask_app
from iva import Iva
from slack_client.handler import SlackClientHandler
from websocket.server import WebSocketServer


def main():
    print('Starting IVA...')
    load_dotenv()

    event_queue = Queue()

    event_scheduler = EventScheduler(event_queue)
    event_scheduler.start()

    frontend_socket_server = WebSocketServer('0.0.0.0', 5678)
    frontend_socket_server.start()

    slack_client_token = os.environ.get('SLACK_CLIENT_TOKEN')
    slack_client = SlackClientHandler(slack_client_token, event_scheduler)
    slack_client.start()

    iva = Iva(event_queue, event_scheduler, frontend_socket_server, slack_client)
    iva.start()

    # event_scheduler.schedule_event(CommandEvent(command='start_morning_routine'))
    # event_scheduler.schedule_timed_event(DailyTimedEvent(StartMorningRoutineEvent(), datetime.datetime.now() + timedelta(seconds=5)))

    flask_app.iva = iva
    threading.Thread(target=flask_app.run, kwargs={'debug': True, 'use_reloader': False}).start()


main()
