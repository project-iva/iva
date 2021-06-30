import datetime
import os
import threading
from collections import deque
from datetime import timedelta
from queue import Queue

from backend_client.client import BackendClient
from event_scheduler import EventScheduler
from events.events import StartMorningRoutineEvent, StartEveningRoutineEvent, CommandEvent
from events.timed_events import DailyTimedEvent
from slack_client.handler import SlackClientHandler
from websocket.server import WebSocketServer
from http_server.http_server import SimpleHTTPServer
from iva import Iva
from dotenv import load_dotenv


def main():
    print('Starting IVA...')
    load_dotenv()

    event_queue = Queue()
    awaited_event_uuids = deque()

    event_scheduler = EventScheduler(event_queue)
    event_scheduler.start()

    frontend_socket_server = WebSocketServer('0.0.0.0', 5678)
    frontend_socket_server.start()

    slack_client_token = os.environ.get('SLACK_CLIENT_TOKEN')
    slack_client = SlackClientHandler(slack_client_token, event_scheduler)
    slack_client.start()

    iva = Iva(event_queue, awaited_event_uuids, event_scheduler, frontend_socket_server, slack_client)
    iva.start()

    # event_scheduler.schedule_event(CommandEvent(command='start_morning_routine'))
    # event_scheduler.schedule_timed_event(DailyTimedEvent(StartMorningRoutineEvent(), datetime.datetime.now() + timedelta(seconds=5)))

    server = SimpleHTTPServer(awaited_event_uuids, event_queue)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()


main()
