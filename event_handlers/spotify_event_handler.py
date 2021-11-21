from queue import Queue
from threading import Thread

from events.events import SpotifyEvent
from intent_helpers.spotify_client_wrapper import SpotifyClientWrapper


class SpotifyEventHandler(Thread):
    """
    Handles spotify actions, such as play/pause
    """

    def __init__(self, event_queue: Queue, spotify_client: SpotifyClientWrapper):
        super().__init__()
        self.event_queue = event_queue
        self.spotify_client = spotify_client

    def run(self):
        while True:
            event: SpotifyEvent = self.event_queue.get()
            print(f'Handling {event}')
            if event.action == SpotifyEvent.Action.PLAY:
                self.spotify_client.play()
            elif event.action == SpotifyEvent.Action.STOP:
                self.spotify_client.stop()
            else:
                print(f'Unknown spotify action: {event.action}')
