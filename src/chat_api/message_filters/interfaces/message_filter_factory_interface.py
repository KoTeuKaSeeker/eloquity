from abc import ABC, abstractmethod
from src.chat_api.message_filters.interfaces.message_filter_interface import MessageFilterInterface

class MessageFilterFactoryInterface(ABC):
    @abstractmethod
    def create_filter(self, filter_type: str, args: dict = {}) -> MessageFilterInterface:
        pass