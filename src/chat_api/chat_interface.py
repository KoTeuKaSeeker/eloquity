from typing import Dict, List
from abc import ABC, abstractmethod

class ChatInterface(ABC):
    @abstractmethod
    def send_message_to_query(self, message: str):
        pass

    @abstractmethod
    def get_handler_states(self, states: Dict[]):


    def handle_message(self, message: str, user_id: int):

