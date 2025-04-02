from typing import Dict
from src.commands.transcibe_llm_command import TranscibeLLMCommand
from src.AI.llm.llm_interface import LLMInterface
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface
from src.transcribers.transcriber_interface import TranscriberInterface
from src.chat_api.message_handler import MessageHandler
from src.chat_api.chat.chat_interface import ChatInterface

class SummuryLLMCommand(TranscibeLLMCommand):
    def __init__(self, model: LLMInterface, filter_factory: MessageFilterFactoryInterface, transcriber: TranscriberInterface, temp_path: str, entry_point_state: str):
        super().__init__(model, filter_factory, transcriber, temp_path, entry_point_state) 
        self.chatting_state = "summury_llm_command.chatting_state"

    async def after_transcribe_message(self, message: dict, context: dict, chat: ChatInterface):
        if "model_context" not in context["chat_data"]:
            context["chat_data"]["model_context"] = ""
        transcription = context["chat_data"]["model_context"]
        response = self.model.get_response(f"Сделай краткое содержание следующей беседы (она может быть неинформативна или вообще пустой, если так - тогда просто так и опиши её):\n{transcription}")

        await chat.send_message_to_query("✒️ Краткое содержание беседы из аудиозаписи:")
        await chat.send_message_to_query(response)
        await chat.send_message_to_query("⏮️ Сейчас вы можете продолжить беседу с ботом - он имеет транскрибацию в памяти.")

        return chat.move_next(context, self.chatting_state)