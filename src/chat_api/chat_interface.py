from abc import ABC, abstractmethod
from chat_api.message_handlers.message_handler_interface import MessageHandlerInterface

class ChatInterface(ABC):
    @abstractmethod
    async def send_message_to_query(self, message: str):
        pass

    @abstractmethod
    async def send_file_to_query(self, file_path: str):
        pass        
