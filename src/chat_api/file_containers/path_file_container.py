from telegram import Message
from src.format_handlers_manager import FormatHandlersManager
from src.chat_api.file_containers.file_container_interface import FileContainerInterface


class PathFileContainer(FileContainerInterface):
    file_path: str

    def __init__(self, file_path: str):
        self.file_path = file_path
    
    async def get_file_path(self):
        return self.file_path

