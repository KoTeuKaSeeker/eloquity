from typing import Callable, Tuple
from src.chat_api.message_handlers.message_handler_interface import MessageHandlerInterface
from src.chat_api.message_filters.message_filter_interface import MessageFilterInterface

class MockMessageHandler(MessageHandlerInterface):
    message_filter: MessageFilterInterface
    handler: Callable[[dict, str, int], str]

    def __init__(self, message_filter: MessageFilterInterface, handler: Callable[[dict, str, int], str]):
        self.message_filter = message_filter
        self.handler = handler
    
    def get_message_filter(self) -> MessageFilterInterface:
        return self.message_filter

    def preprocess_message(self, message: dict, message_type: str, user_id: int) -> Tuple[dict, str, int]:
        """
            Возвращает состояние, в которое переходит диалог.
        """
        return message, message_type, user_id

    def get_message_handler(self) -> Callable[[dict, str, int], str]:
        return self.handler
