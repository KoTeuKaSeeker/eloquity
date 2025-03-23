from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface

from src.chat_api.message_filters.base_filters.all_message_filter import AllMessageFilter
from src.chat_api.message_filters.interfaces.message_filter_interface import MessageFilterInterface
from src.chat_api.message_filters.base_filters.text_message_filter import TextMessageFilter
from src.chat_api.message_filters.base_filters.audio_message_filter import AudioMessageFilter
from src.chat_api.message_filters.base_filters.regex_message_filter import RegexMessageFilter
from src.chat_api.message_filters.base_filters.command_message_filter import CommandMessageFilter



class BaseMessageFilterFactory(MessageFilterFactoryInterface):
    def create_filter(self, filter_type: str, args: dict = {}) -> MessageFilterInterface:
        fabric = {
            "all": AllMessageFilter,
            "command": CommandMessageFilter,
            "text": TextMessageFilter,
            "audio": AudioMessageFilter,
            "voice": AudioMessageFilter,
            "video": AudioMessageFilter,
            "document": AudioMessageFilter,
            "document.all": AudioMessageFilter,
            "regex": RegexMessageFilter
        }
        
        return fabric[filter_type](**args)
