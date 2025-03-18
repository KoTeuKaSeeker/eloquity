from src.chat_api.message_filters.base_filters.base_message_filter import BaseMessageFilter
import re

class CommandMessageFilter(BaseMessageFilter):
    command: str

    def __init__(self, command: str):
        self.command = command

    def filter(self, message: dict) -> bool:
        if "text" not in message:
            return False
        
        matches = re.findall(r"^/" + self.command + r"(?:@\w+)?\b", message["text"])
        if len(matches) == 0:
            return False
        return True
        