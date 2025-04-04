from typing import List
from src.chat_api.message_filters.base_filters.base_message_filter import BaseMessageFilter

class EqualMessageFilter(BaseMessageFilter):
    messages: List[str]
    
    def __init__(self, messages: List[str]):
        self.messages = messages

    def filter(self, message: dict) -> bool:
        if "text" in message and any(message["text"] == m for m in self.messages):
            return True
        return False
        