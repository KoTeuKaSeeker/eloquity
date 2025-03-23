from src.chat_api.message_filters.base_filters.base_message_filter import BaseMessageFilter
import re

class AudioMessageFilter(BaseMessageFilter):
    def filter(self, message: dict) -> bool:
        if "audio_container" not in message:
            return False
        return True
        