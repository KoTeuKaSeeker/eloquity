from telegram import Message
from src.format_handlers_manager import FormatHandlersManager
from src.chat_api.file_containers.file_container_interface import FileContainerInterface
from src.exeptions.telegram_exceptions.too_big_file_exception import TooBigFileException
from src.exeptions.telegram_exceptions.telegram_bot_exception import TelegramBotException
from src.drop_box_manager import DropBoxManager


class TelegramFileContainer(FileContainerInterface):
    telegram_message: Message
    file_path: str
    format_handler_manager: FormatHandlersManager
    context: dict
    dropbox_manager: DropBoxManager

    def __init__(self, context: dict, telegram_message: Message, format_handler_manager: FormatHandlersManager, dropbox_manager: DropBoxManager):
        self.telegram_message = telegram_message
        self.format_handler_manager = format_handler_manager
        self.file_path = None
        self.context = context
        self.dropbox_manager = dropbox_manager
    
    async def get_file_path(self):
        if self.file_path is None:
            self.file_path = await self.format_handler_manager.load_audio(self.telegram_message)
            
        return self.file_path

