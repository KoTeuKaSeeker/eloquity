from typing import List, Dict
from src.commands.command_interface import CommandInterface
from src.chat_api.message_handler import MessageHandler
from src.AI.llm.llm_interface import LLMInterface
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface
from src.chat_api.chat.chat_interface import ChatInterface

class LLMCommand(CommandInterface):
    model: LLMInterface
    system_prompt: str

    def __init__(self, model: LLMInterface, filter_factory: MessageFilterFactoryInterface):
        self.model = model
        self.filter_factory = filter_factory
        self.chatting_state = "llm_command.chatting_state"
        self.system_prompt = ""
    
    async def handle_message_by_model(self, message: dict, context: dict, chat: ChatInterface):
        text = message["text"]
        
        if "messages_history" not in context["chat_data"]:
            context["chat_data"]["messages_history"] = [{"role": "system", "content": self.system_prompt}]
        messages_history: List[dict] = context["chat_data"]["messages_history"]

        user_message = {"role": "user", "content": text}

        messages_history.append(user_message)

        model_response = self.model.get_response(messages_history)
        messages_history.append(model_response)

        await chat.send_message_to_query(model_response["content"])        
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
    