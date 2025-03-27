from typing import List, Dict
from src.commands.command_interface import CommandInterface
from src.chat_api.message_handler import MessageHandler
from src.AI.llm.llm_interface import LLMInterface
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface
from src.chat_api.chat.chat_interface import ChatInterface


class LLMCommand(CommandInterface):
    model: LLMInterface

    def __init__(self, model: LLMInterface, filter_factory: MessageFilterFactoryInterface):
        self.model = model
        self.filter_factory = filter_factory
        self.chatting_state = "llm_command.chatting_state"
    
    async def handle_message_by_model(self, message: dict, context: dict, chat: ChatInterface):
        text = message["text"]
        
        if "messages_history" not in context["user_data"]:
            context["user_data"]["messages_history"] = []
        messages_history = context["user_data"]["messages_history"]

        messages_history.append(f"[USER]: {text}")

        if "model_context" not in context["user_data"]:
            context["user_data"]["model_context"] = ""
        model_context = context["user_data"]["model_context"]

        dialog = "\n".join(messages_history)
        content = f"Контекстная информация:\n{model_context}\n\nТы ведёшь диалог с пользователем [USER] от имени [BOT]. Диалог может быть пустым, может содержать вопросы от пользователя - просто веди с ним беседу. Вот диалог:\n{dialog}\n\n Твой ответ:\n[BOT]: "

        model_response = self.model.get_response(content)
        messages_history.append(f"[BOT]: {model_response}")

        await chat.send_message_to_query(model_response)        
        return chat.stay_on_state(context)

    async def cancel_command(self, message: dict, context: dict, chat: ChatInterface):
        await chat.send_message_to_query("🔖 Режим общения с ботом выключен.")
        return chat.move_next(context, "entry_point", self.chatting_state)

    def get_conversation_states(self) -> Dict[str, MessageHandler]:
        return {
            self.chatting_state: [
                MessageHandler(self.filter_factory.create_filter("text"), self.handle_message_by_model),
                MessageHandler(self.filter_factory.create_filter("command", dict(command="cancel")), self.handle_message_by_model)
            ]
        }
    