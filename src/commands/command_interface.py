from abc import ABC, abstractmethod
from typing import List, Dict
from chat_api.message_handlers.message_handler_interface import MessageHandlerInterface
from src.chat_api.message_filters.message_filter_interface import MessageFilterInterface

class CommandInterface(ABC):
    def get_entry_points(self) -> List[MessageHandlerInterface]:
        return []

    def get_conversation_states(self) -> Dict[str, MessageHandlerInterface]:
        return {}