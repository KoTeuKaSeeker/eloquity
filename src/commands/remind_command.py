from typing import List
from src.commands.command_interface import CommandInterface
from src.conversation.conversation_states_manager import ConversationState
from src.chat_api.chat_interface import ChatInterface
from src.chat_api.message_handlers.message_handler_interface import MessageHandlerInterface
from src.chat_api.message_filters.message_filter_interface import MessageFilterInterface

class RemindCommand(CommandInterface):
    def __init__(self):
        pass
    
    async def handle_command(self, message: dict, message_type: str, context: dict, chat: ChatInterface):
        await chat.send_message_to_query("⏮️ Для начала работы с ботом выполните команду /start")

    def get_entry_points(self) -> List[MessageHandlerInterface]:
        return [MessageHandlerInterface.from_filter(MessageFilterInterface.from_str("all"), self.handle_command)]