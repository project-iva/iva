from dataclasses import dataclass

import requests

from models.json_model import JsonDecodableModel


@dataclass
class Joke(JsonDecodableModel):
    joke: str

    @classmethod
    def from_dict(cls, d):
        return cls(d.get('joke'))


class JokesAPIWrapper:
    @staticmethod
    def fetch_joke() -> Joke:
        joke_response = requests.get('https://v2.jokeapi.dev/joke/Any?type=single')
        return Joke.from_dict(joke_response.json())
