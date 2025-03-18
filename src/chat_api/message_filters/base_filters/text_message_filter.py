from src.chat_api.message_filters.base_filters.base_message_filter import BaseMessageFilter
import re

class TextMessageFilter(BaseMessageFilter):
    def filter(self, message: dict) -> bool:
        if "text" not in message:
            return False
        return True
        