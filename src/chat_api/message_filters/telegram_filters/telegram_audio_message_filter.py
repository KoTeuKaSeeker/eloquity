from src.chat_api.message_filters.telegram_filters.telegram_message_filter import TelegramMessageFilter
import re

class TelegramAudioMessageFilter(TelegramMessageFilter):
    def filter(self, message: dict) -> bool:
        if "audio_path" not in message:
            return False
        return True
        