from src.chat_api.message_filters.telegram_filters.telegram_message_filter import TelegramMessageFilter
import re

class TelegramTextMessageFilter(TelegramMessageFilter):
    def filter(self, message: dict) -> bool:
        if "text" not in message:
            return False
        return True
        