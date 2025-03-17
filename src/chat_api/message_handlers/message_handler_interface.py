from typing import Tuple, Callable
from abc import ABC, abstractmethod
from src.chat_api.message_filters.message_filter_interface import MessageFilterInterface
from chat_api.chat.chat_interface import ChatInterface

class MessageHandlerInterface(ABC):
    @abstractmethod
    @classmethod
    def from_filter(cls, message_filter: MessageFilterInterface, handler: Callable[[dict, dict, ChatInterface], str]):
        pass

    @abstractmethod
    def get_message_filter(self) -> MessageFilterInterface:
        pass

    @abstractmethod
    async def preprocess_message(self, message: dict, context: dict, chat: ChatInterface) -> Tuple[dict, dict, ChatInterface]:
        """
            Возвращает состояние, в которое переходит диалог.
        """
        pass

    @abstractmethod
    def get_message_handler(self) -> Callable[[dict, dict, ChatInterface], str]:
        pass
