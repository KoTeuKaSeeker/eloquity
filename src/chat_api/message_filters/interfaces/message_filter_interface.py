from abc import ABC, abstractmethod

class MessageFilterInterface(ABC):
    @classmethod
    def from_str(cls, filter_name: str, filter_args: dict = {}):
        pass

    @abstractmethod
    def filter(self, message: dict) -> bool:
        pass