from telegram import Message
from src.format_handlers_manager import FormatHandlersManager
from src.chat_api.file_containers.file_container_interface import FileContainerInterface


class TelegramFileContainer(FileContainerInterface):
    telegram_message: Message
    file_path: str
    format_handler_manager: FormatHandlersManager

    def __init__(self, telegram_message: Message, format_handler_manager: FormatHandlersManager):
        self.telegram_message = telegram_message
        self.format_handler_manager = format_handler_manager
        self.file_path = None
    
    async def get_file_path(self):
        if self.file_path is None:
            self.file_path = await self.format_handler_manager.load_audio(self.telegram_message)
        return self.file_path

