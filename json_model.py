import json
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, asdict


@dataclass
class JsonModel(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def from_dict(cls, d):
        pass

    @classmethod
    def from_json(cls, j):
        return cls.from_dict(json.loads(j))

    def to_json(self) -> str:
        return json.dumps(asdict(self))
