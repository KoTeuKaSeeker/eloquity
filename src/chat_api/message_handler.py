from typing import Callable, Tuple
from src.chat_api.chat.chat_interface import ChatInterface
from src.chat_api.message_filters.interfaces.message_filter_interface import MessageFilterInterface

class MessageHandler():
    message_filter: MessageFilterInterface
    handler: Callable[[dict, dict, ChatInterface], str]

    def __init__(self, message_filter: MessageFilterInterface, handler: Callable[[dict, dict, ChatInterface], str]):
        self.message_filter = message_filter
        self.handler = handler

    def get_message_filter(self) -> MessageFilterInterface:
        return self.message_filter

    async def preprocess_message(self, message: dict, context: dict, chat: ChatInterface) -> Tuple[dict, dict, ChatInterface]:
        """
            Возвращает состояние, в которое переходит диалог.
        """
        return message, context, chat

    def get_message_handler(self) -> Callable[[dict, dict, ChatInterface], str]:
        return self.handler