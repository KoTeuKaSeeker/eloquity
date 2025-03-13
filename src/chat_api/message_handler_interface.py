from abc import ABC, abstractmethod
from src.chat_api.message_filter_interface import MessageFilterInterface

class MessageHandlerInterface(ABC):
    @abstractmethod
    def handle_message(self, message: dict, message_type: str, user_id: int) -> str:
        """
            Возвращает состояние, в которое переходит диалог.
        """
        pass

    @abstractmethod
    def get_message_filter(self) -> MessageFilterInterface:
        pass
