from src.chat_api.message_filters.base_filters.base_message_filter import BaseMessageFilter

class AllMessageFilter(BaseMessageFilter):
    def filter(self, message: dict) -> bool:
        return True
        