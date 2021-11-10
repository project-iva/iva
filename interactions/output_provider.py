from abc import ABC, abstractmethod


class OutputProvider(ABC):
    @abstractmethod
    def output(self, output: str):
        pass
