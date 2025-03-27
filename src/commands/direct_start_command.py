from typing import List, Dict
from src.commands.command_interface import CommandInterface
from src.chat_api.chat.chat_interface import ChatInterface
from src.chat_api.message_handler import MessageHandler
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface

class DirectStartCommand(CommandInterface):
    direction_states: dict[str, str]
    
    def __init__(self, filter_factory: MessageFilterFactoryInterface, direction_states: dict[str, str]):
        self.filter_factory = filter_factory
        self.direction_states = direction_states
    
    async def handle_command(self, message: dict, context: dict, chat: ChatInterface):
        model_name = context["model_name"]
        await chat.send_message_to_query(f"Привет 👋. Бот {model_name} готов к взаимодействию 😉!")
        
        state = self.direction_states[model_name]
        return chat.move_next(context, state)
    
    async def message_to_write_start(self, message: dict, context: dict, chat: ChatInterface):
        model_name = context["model_name"]
        await chat.send_message_to_query(f"⏮️ Вы сейчас используйте бота {model_name}. Чтобы продолжить работу с {model_name}, выполните команду /start")
        return chat.stay_on_state(context)


    def get_entry_points(self) -> List[MessageHandler]:
        return [MessageHandler(self.filter_factory.create_filter("command", dict(command="start")), self.handle_command)]
    
    def get_conversation_states(self) -> Dict[str, MessageHandler]:
        return {
            "entry_point": [
                MessageHandler(self.filter_factory.create_filter("command", dict(command="start")), self.handle_command),
                MessageHandler(self.filter_factory.create_filter("all"), self.message_to_write_start)
            ]
        }