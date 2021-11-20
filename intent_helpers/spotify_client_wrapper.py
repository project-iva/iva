import asyncio
import os

import spotify
from spotify import Device


class SpotifyException(Exception):
    pass


class SpotifyClientWrapper:
    def __init__(self):
        client_id = os.environ.get('SPOTIFY_CLIENT_ID')
        client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
        access_token = os.environ.get('SPOTIFY_ACCESS_TOKEN')
        refresh_token = os.environ.get('SPOTIFY_REFRESH_TOKEN')
        target_device_name = os.environ.get('SPOTIFY_TARGET_DEVICE_NAME')
        self.loop = asyncio.new_event_loop()
        self.http_client = spotify.http.HTTPUserClient(client_id, client_secret, access_token, refresh_token, self.loop)
        self.target_device = self.get_target_device(target_device_name)

    def get_target_device(self, target_device_name: str) -> Device:
        devices_data = self.loop.run_until_complete(self.http_client.available_devices())
        devices = [Device(item) for item in devices_data["devices"]]
        matching_devices = [device for device in devices if device.name == target_device_name]
        if len(matching_devices) != 1:
            raise SpotifyException
        return matching_devices[0]

    def play(self):
        # refresh device status
        self.target_device = self.get_target_device(self.target_device.name)
        task = None
        if self.target_device.is_active:
            # play
            task = self.http_client.play_playback(None, device_id=self.target_device.id)
        else:
            # transfer playback
            task = self.http_client.transfer_player(device_id=self.target_device.id, play=True)
        self.loop.run_until_complete(task)

    def stop(self):
        self.loop.run_until_complete(self.http_client.pause_playback(device_id=self.target_device.id))
