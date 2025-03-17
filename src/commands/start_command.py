from typing import List
from src.commands.command_interface import CommandInterface
from chat_api.chat.chat_interface import ChatInterface
from src.chat_api.message_handlers.message_handler_interface import MessageHandlerInterface
from src.chat_api.message_filters.message_filter_interface import MessageFilterInterface

class StartCommand(CommandInterface):
    def __init__(self):
        pass
    
    async def handle_command(self, message: dict, context: dict, chat: ChatInterface):
        await chat.send_message_to_query("Привет 👋. Это бот для анализа аудио и видео сообщений и извлечения из них информации по задаче.")
        context["context"]['state_stack'] = ["entry_point"]
        context["context"]['state'] = "entry_point"
        return "entry_point"

    def get_entry_points(self) -> List[MessageHandlerInterface]:
        return [MessageHandlerInterface.from_filter(MessageFilterInterface.from_str("command", dict(command="start")), self.handle_command)]