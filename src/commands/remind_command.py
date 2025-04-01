from typing import List, Dict
from src.commands.command_interface import CommandInterface
from src.chat_api.chat.chat_interface import ChatInterface
from src.chat_api.message_handler import MessageHandler
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface

class RemindCommand(CommandInterface):
    def __init__(self, filter_factory: MessageFilterFactoryInterface):
        self.filter_factory = filter_factory
    
    async def handle_command(self, message: dict, context: dict, chat: ChatInterface):
        await chat.send_message_to_query("⏮️ Для начала работы с ботом выполните команду /start")

    def get_conversation_states(self) -> Dict[str, MessageHandler]:
        return {
            "entry_point": [
                MessageHandler(self.filter_factory.create_filter("all"), self.handle_command)
            ]
        }