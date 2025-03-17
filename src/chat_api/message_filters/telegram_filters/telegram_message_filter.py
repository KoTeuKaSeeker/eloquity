from abc import ABC, abstractmethod
from src.chat_api.message_filters.message_filter_interface import MessageFilterInterface
from src.chat_api.message_filters.telegram_filters.telegram_command_message_filter import TelegramCommandMessageFilter
from src.chat_api.message_filters.telegram_filters.telegram_text_message_filter import TelegramTextMessageFilter
from src.chat_api.message_filters.telegram_filters.telegram_audio_message_filter import TelegramAudioMessageFilter
from src.chat_api.message_filters.telegram_filters.telegram_regex_message_filter import TelegramRegexMessageFilter

class TelegramMessageFilter(MessageFilterInterface):
    @classmethod
    def from_str(cls, filter_name: str, filter_args: dict = {}):
        fabric = {
            "command": TelegramCommandMessageFilter(*filter_args),
            "text": TelegramTextMessageFilter(*filter_args),
            "audio": TelegramAudioMessageFilter(*filter_args),
            "voice": TelegramAudioMessageFilter(*filter_args),
            "video": TelegramAudioMessageFilter(*filter_args),
            "document": TelegramAudioMessageFilter(*filter_args),
            "document.all": TelegramAudioMessageFilter(*filter_args),
            "regex": TelegramRegexMessageFilter(*filter_args)
        }

        return fabric[filter_name]

    @abstractmethod
    def filter(self, message: dict) -> bool:
        pass