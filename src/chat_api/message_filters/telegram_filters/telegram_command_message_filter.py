from src.chat_api.message_filters.telegram_filters.telegram_message_filter import TelegramMessageFilter
import re

class TelegramCommandMessageFilter(TelegramMessageFilter):
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
        