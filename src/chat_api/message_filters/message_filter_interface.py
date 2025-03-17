from abc import ABC, abstractmethod
from src.chat_api.message_filters.inverted_filter import InvertedFilter

class MessageFilterInterface(ABC):
    @abstractmethod
    @classmethod
    def from_str(cls, filter_name: str, filter_args: dict = {}):
        pass

    @abstractmethod
    def filter(self, message: dict) -> bool:
        pass

    def __invert__(self):
        return InvertedFilter(self)