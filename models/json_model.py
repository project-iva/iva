import json
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, asdict


@dataclass
class JsonEncodableModel(metaclass=ABCMeta):
    @property
    def json(self) -> str:
        return json.dumps(self.dict)

    @property
    def dict(self) -> dict:
        return asdict(self)


@dataclass
class JsonDecodableModel(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def from_dict(cls, d):
        pass

    @classmethod
    def from_json(cls, j):
        return cls.from_dict(json.loads(j))


@dataclass
class JsonModel(JsonEncodableModel, JsonDecodableModel, metaclass=ABCMeta):
    pass
