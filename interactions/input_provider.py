from abc import ABC, abstractmethod


class InputProvider(ABC):
    @abstractmethod
    def get_input(self) -> str:
        pass
