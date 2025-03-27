from typing import List, Dict
from src.commands.command_interface import CommandInterface
from src.chat_api.chat.chat_interface import ChatInterface
from src.chat_api.message_handler import MessageHandler
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface
import re

class DirectStartCommand(CommandInterface):
    direction_states: dict[str, str]
    
    def __init__(self, filter_factory: MessageFilterFactoryInterface, direction_states: dict[str, str]):
        self.filter_factory = filter_factory
        self.direction_states = direction_states
    
    async def select_bot_message(self, context: dict, chat: ChatInterface):
        model_names = list(self.direction_states.keys())
        model_names_str = "\n".join([f"{i + 1}. {name}" for i, name in enumerate(model_names)])
        await chat.send_message_to_query(f"💎 Выбирете номер бота, которого вы хотите использовать:\n{model_names_str}")    
        return chat.move_next(context, "select_bot_state")

    async def handle_command(self, message: dict, context: dict, chat: ChatInterface):
        if "model_name" in context["user_data"]:
            model_name = context["user_data"]["model_name"]
            await chat.send_message_to_query(f"Привет 👋. Бот {model_name} готов к взаимодействию 😉!")
            
            state = self.direction_states[model_name]
            return chat.move_next(context, state)
        else:
            return await self.select_bot_message(context, chat)
    
    async def message_to_write_start(self, message: dict, context: dict, chat: ChatInterface):
        model_name = None
        if "model_name" in context["user_data"]: 
            model_name = context["user_data"]["model_name"]
            await chat.send_message_to_query(f"⏮️ Вы сейчас используйте бота {model_name}. Чтобы продолжить работу с {model_name}, выполните команду /start")
            return chat.stay_on_state(context)
        else:
            return await self.select_bot_message(context, chat)
    
    async def select_bot_command(self, message: dict, context: dict, chat: ChatInterface):
        model_id = int(re.findall(r"\d+", message["text"])[0]) - 1

        model_names = list(self.direction_states.keys())
        if  model_id < 0 or model_id >= len(model_names):
            model_names_str = "\n".join([f"{i + 1}. {name}" for i, name in enumerate(model_names)])
            await chat.send_message_to_query(f"🎃 Вы указали неверный номер модели. Выбирете номер бота, которого вы хотите использовать среди следующих значений:\n{model_names_str}")
            return chat.stay_on_state(context)

        model_name = list(self.direction_states.keys())[model_id]
        context["user_data"]["model_name"] = model_name

        await chat.send_message_to_query(f"🔖 Вы выбрали бота {model_id + 1}. {model_name}. Выполните команду /start для продолжения работы с ботом.\n🔎 Если вы хотите поменять бота, выполните команду /change_bot.")

        return chat.move_back(context)

    async def change_bot_command(self, message: dict, context: dict, chat: ChatInterface):
        return await self.select_bot_message(context, chat)

    async def wrong_select_bot_text(self, message: dict, context: dict, chat: ChatInterface):
        model_names = list(self.direction_states.keys())
        model_names_str = "\n".join([f"{i + 1}. {name}" for i, name in enumerate(model_names)])
        await chat.send_message_to_query(f"⏮️ Вы ввели некорректное значение номера бота. Выбирете номер бота, которого вы хотите использовать среди следующих значений:\n{model_names_str}")
        return chat.stay_on_state(context)
    
    def get_conversation_states(self) -> Dict[str, MessageHandler]:
        return {
            "entry_point": [
                MessageHandler(self.filter_factory.create_filter("command", dict(command="start")), self.handle_command),
                MessageHandler(self.filter_factory.create_filter("command", dict(command="change_bot")), self.change_bot_command),
                MessageHandler(self.filter_factory.create_filter("all"), self.message_to_write_start)
            ],
            "select_bot_state": [
                MessageHandler(self.filter_factory.create_filter("regex", dict(pattern=r"\d+")), self.select_bot_command),
                MessageHandler(self.filter_factory.create_filter("all"), self.wrong_select_bot_text)
            ]
        }