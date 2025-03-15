from typing import List
from src.commands.command_interface import CommandInterface
from src.conversation.conversation_states_manager import ConversationState
from src.chat_api.chat_interface import ChatInterface
from src.chat_api.message_handlers.message_handler_interface import MessageHandlerInterface
from src.chat_api.message_filters.message_filter_interface import MessageFilterInterface

class StartCommand(CommandInterface):
    def __init__(self):
        pass
    
    async def handle_command(self, message: dict, message_type: str, context: dict, chat: ChatInterface):
        await chat.send_message_to_query("Привет 👋. Это бот для анализа аудио и видео сообщений и извлечения из них информации по задаче.")
        context["context"]['state_stack'] = [ConversationState.waiting]
        context["context"]['state'] = ConversationState.waiting
        return str(ConversationState.waiting.value)

    def get_entry_points(self) -> List[MessageHandlerInterface]:
        return [MessageHandlerInterface.from_filter(MessageFilterInterface.from_str("command", dict(command="start")), self.handle_command)]