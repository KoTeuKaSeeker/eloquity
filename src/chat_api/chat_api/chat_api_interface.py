from abc import ABC, abstractmethod
from typing import Dict, List
from src.chat_api.message_handlers.message_handler_interface import MessageHandlerInterface

class ChatApiInterface(ABC):
    @abstractmethod
    def set_handler_states(self, handler_states: Dict[str, List[MessageHandlerInterface]]):
        pass

    @abstractmethod
    def start(self, poll_interval: int = 3):
        pass