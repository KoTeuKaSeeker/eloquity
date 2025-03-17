from src.chat_api.message_filters.message_filter_interface import MessageFilterInterface

class InvertedFilter(MessageFilterInterface):
    message_filter: MessageFilterInterface

    def __init__(self, message_filter: MessageFilterInterface):
        self.message_filter = message_filter

    @classmethod
    def from_str(cls, filter_name: str, filter_args: dict = {}):
        return None

    def filter(self, message: dict, user_id: int) -> bool:
        return not self.message_filter.filter(message, user_id)

    def __invert__(self):
        return InvertedFilter(self)