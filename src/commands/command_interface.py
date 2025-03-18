from abc import ABC, abstractmethod
from typing import List, Dict
from src.chat_api.message_handler import MessageHandler
from src.chat_api.message_handler import MessageHandler

class CommandInterface(ABC):
    def get_entry_points(self) -> List[MessageHandler]:
        return []

    def get_conversation_states(self) -> Dict[str, MessageHandler]:
        return {}