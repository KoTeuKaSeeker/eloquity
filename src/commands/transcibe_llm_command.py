from typing import Dict
from src.commands.llm_command import LLMCommand
from src.AI.llm.llm_interface import LLMInterface
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface
from src.chat_api.message_handler import MessageHandler
from src.chat_api.chat.chat_interface import ChatInterface
from src.transcribers.transcriber_interface import TranscriberInterface
from src.chat_api.file_containers.file_container_interface import FileContainerInterface
import os
import uuid

class TranscibeLLMCommand(LLMCommand):
    transcriber: TranscriberInterface
    temp_path: str

    def __init__(self, model: LLMInterface, filter_factory: MessageFilterFactoryInterface, transcriber: TranscriberInterface, temp_path: str):
        super().__init__(model, filter_factory)

        self.transcriber = transcriber
        self.temp_path = temp_path
        self.transcribe_state = "entry_point" 
        self.chatting_state = "transcribe_llm_command.chatting_state"
    
    async def transcirbe_audio(self, message: dict, context: dict, chat: ChatInterface):
        audio_container: FileContainerInterface = message["audio_container"]
        file_path = await audio_container.get_file_path()

        transcribe_result = self.transcriber.transcript_audio(file_path)
        transcription = "\n".join(f"speaker_{segment.speaker_id}: {segment.text}" for segment in transcribe_result.segments)
        
        transcription_name = str(uuid.uuid4())
        transcription_path = os.path.join(self.temp_path, transcription_name)
        with open(transcription_path, "w", encoding="utf-8") as file:
            file.write(transcription)

        await chat.send_message_to_query("🚀 Транскрибация успешно завершена:")
        await chat.send_file_to_query(transcription_path)

        context["user_data"]["model_context"] = transcription
        await self.after_transcribe_message(message, context, chat)

        # return chat.move_next(context, self.chatting_state, self.transcribe_state)
        return self.transcribe_state
    
    async def after_transcribe_message(self, message: dict, context: dict, chat: ChatInterface):
        await chat.send_message_to_query("⏮️ Сейчас можете продолжить беседу с ботом - он имеет транскрибацию в памяти.")

    async def waiting_audio_message(self, message: dict, context: dict, chat: ChatInterface):
        await chat.send_message_to_query("⏮️ Отправьте аудиозапись для продолжения взаимодействия с ботом.")
        return chat.stay_on_state(context)

    def get_conversation_states(self) -> Dict[str, MessageHandler]:
        states = super().get_conversation_states()
        
        states[self.transcribe_state] = [
            MessageHandler(self.filter_factory.create_filter("audio"), self.transcirbe_audio),
            MessageHandler(self.filter_factory.create_filter("voice"), self.transcirbe_audio),
            MessageHandler(self.filter_factory.create_filter("video"), self.transcirbe_audio),
            MessageHandler(self.filter_factory.create_filter("all"), self.waiting_audio_message),
        ]

        return states