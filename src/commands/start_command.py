from typing import List, Dict
from src.commands.command_interface import CommandInterface
from src.chat_api.chat.chat_interface import ChatInterface
from src.chat_api.message_handler import MessageHandler
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface

class StartCommand(CommandInterface):
    def __init__(self, filter_factory: MessageFilterFactoryInterface):
        self.filter_factory = filter_factory
    
    async def handle_command(self, message: dict, context: dict, chat: ChatInterface):
        await chat.send_message_to_query("Привет 👋. Это бот для анализа аудио и видео сообщений и извлечения из них информации по задаче.")
        context["context"]['state_stack'] = ["entry_point"]
        context["context"]['state'] = "entry_point"
        return "entry_point"

    def get_conversation_states(self) -> Dict[str, MessageHandler]:
        return {
            "entry_point": [
                MessageHandler(self.filter_factory.create_filter("command", dict(command="start")), self.handle_command)
            ]
        }