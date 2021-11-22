from abc import ABC, abstractmethod


class OutputProvider(ABC):
    """
    Interface for output providers
    """

    @abstractmethod
    def output(self, output: str):
        pass
