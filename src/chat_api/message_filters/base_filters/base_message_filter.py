from src.chat_api.message_filters.interfaces.message_filter_interface import MessageFilterInterface
from src.chat_api.message_filters.base_filters.inverted_filter import InvertedFilter

class BaseMessageFilter(MessageFilterInterface):
    def __invert__(self):
        return InvertedFilter(self)
