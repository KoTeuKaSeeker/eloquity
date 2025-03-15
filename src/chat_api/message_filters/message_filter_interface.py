from abc import ABC, abstractmethod
from src.chat_api.message_filters.inverted_filter import InvertedFilter

class MessageFilterInterface(ABC):
    @classmethod
    def from_str(cls, filter_name: str, filter_args: dict = {}):
        pass

    @abstractmethod
    def filter(self, message: dict, message_type: str, user_id: int) -> bool:
        pass

    def __invert__(self):
        return InvertedFilter(self)