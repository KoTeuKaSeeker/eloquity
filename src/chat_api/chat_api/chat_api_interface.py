from abc import ABC, abstractmethod
from typing import Dict, List
from src.chat_api.message_handler import MessageHandler
from typing import Dict, List, Callable, Any

class ChatApiInterface(ABC):
    @abstractmethod
    def set_handler_states(self, handler_states: Dict[str, List[MessageHandler]]):
        pass

    @abstractmethod
    def start(self, poll_interval: int = 3):
        pass