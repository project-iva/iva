from abc import ABC, abstractmethod


class InputProvider(ABC):
    """
    Interface for user input providers
    """

    @abstractmethod
    def get_input(self) -> str:
        pass
