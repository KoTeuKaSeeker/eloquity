from typing import List, Dict
from src.commands.command_interface import CommandInterface
from src.chat_api.chat.chat_interface import ChatInterface
from src.chat_api.message_handler import MessageHandler
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface

class StartCommand(CommandInterface):
    def __init__(self, filter_factory: MessageFilterFactoryInterface, first_state: str, first_keyboard: List[List[str]] = None, first_keyboard_keys: List[List[str]] = None):
        self.filter_factory = filter_factory
        self.first_state = first_state
        self.first_keyboard = first_keyboard
        self.first_keyboard_keys = first_keyboard_keys
    
    async def handle_command(self, message: dict, context: dict, chat: ChatInterface):
        message = "Привет 👋! Я бот для помощи при найме специалистов на основе аудиозаписи интервью. Отправьте аудиозапись, если хотите, чтобы я обработал его 😊"
        if self.first_keyboard is None:
            await chat.remove_keyboad(message)
        else:
            await chat.send_keyboad(message, self.first_keyboard, self.first_keyboard_keys)
        return chat.move_next(context, self.first_state)
    
    async def wrong_message(self, message: dict, context: dict, chat: ChatInterface):
        keyboard = [["/start"]]
        keyboard_keys = [["/start"]]
        await chat.send_keyboad("👻 Для начала работы с ботом выполните команду /start (или нажмите соответствующую кнопку)", keyboard, keyboard_keys)
        return chat.stay_on_state(context)

    def get_conversation_states(self) -> Dict[str, MessageHandler]:
        return {
            "entry_point": [
                MessageHandler(self.filter_factory.create_filter("command", dict(command="start")), self.handle_command),
                MessageHandler(self.filter_factory.create_filter("all"), self.wrong_message)
            ]
        }