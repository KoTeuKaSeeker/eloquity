from typing import Callable, Tuple
from src.chat_api.chat.chat_interface import ChatInterface
from src.chat_api.message_filters.message_filter_interface import MessageFilterInterface
from src.chat_api.message_handlers.message_handler_interface import MessageHandlerInterface

class TelegramMessageHandler(MessageHandlerInterface):
    message_filter: MessageFilterInterface
    handler: Callable[[dict, dict, ChatInterface], str]

    def __init__(self, message_filter: MessageFilterInterface, handler: Callable[[dict, dict, ChatInterface], str]):
        self.message_filter = message_filter
        self.handler = handler

    @classmethod
    def from_filter(cls, message_filter: MessageFilterInterface, handler: Callable[[dict, dict, ChatInterface], str]):
        message_handler = cls(message_filter, handler)
        return message_handler

    def get_message_filter(self) -> MessageFilterInterface:
        return self.message_filter

    async def preprocess_message(self, message: dict, context: dict, chat: ChatInterface) -> Tuple[dict, dict, ChatInterface]:
        """
            Возвращает состояние, в которое переходит диалог.
        """
        return message, context, chat

    def get_message_handler(self) -> Callable[[dict, dict, ChatInterface], str]:
        return self.handler