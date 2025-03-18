from src.chat_api.message_filters.base_filters.base_message_filter import BaseMessageFilter
import re

class RegexMessageFilter(BaseMessageFilter):
    pattern: str

    def __init__(self, pattern: str):
        self.pattern = pattern

    def filter(self, message: dict) -> bool:
        if "text" not in message:
            return False
        
        matches = re.findall(self.pattern, message["text"])
        if len(matches) == 0:
            return False
        return True
        