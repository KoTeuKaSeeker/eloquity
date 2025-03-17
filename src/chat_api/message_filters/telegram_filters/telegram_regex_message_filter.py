from src.chat_api.message_filters.telegram_filters.telegram_message_filter import TelegramMessageFilter
import re

class TelegramRegexMessageFilter(TelegramMessageFilter):
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
        