from src.chat_api.message_filters.interfaces.message_filter_interface import MessageFilterInterface

class InvertedFilter(MessageFilterInterface):
    message_filter: MessageFilterInterface

    def __init__(self, message_filter: MessageFilterInterface):
        self.message_filter = message_filter

    def filter(self, message: dict) -> bool:
        return not self.message_filter.filter(message)

    def __invert__(self):
        return InvertedFilter(self)