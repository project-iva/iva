from threading import Thread

from events.events import SpotifyEvent
from spotify_wrapper.spotify_client_wrapper import SpotifyClientWrapper


class SpotifyEventHandler(Thread):
    def __init__(self, event: SpotifyEvent, spotify_client: SpotifyClientWrapper):
        super().__init__()
        self.event = event
        self.spotify_client = spotify_client

    def run(self):
        print(f'Handling {self.event}')
        if self.event.action == SpotifyEvent.Action.PLAY:
            self.spotify_client.play()
        elif self.event.action == SpotifyEvent.Action.STOP:
            self.spotify_client.stop()
        else:
            print(f'Unknown spotify action: {self.event.action}')
