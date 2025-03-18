from typing import List, Dict
from src.commands.transcribe_audio_command import TranscribeAudioCommand
from src.commands.audio_loaders.message_audio_loader import MessageAudioLoader
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager
from src.commands.audio_loaders.audio_loader_interface import AudioLoaderInterface
from src.bitrix.bitrix_manager import BitrixManager
from src.chat_api.chat.chat_interface import ChatInterface
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface
from src.chat_api.message_handler import MessageHandler

class TranscribeAudioWithPreloadedNamesCommand(TranscribeAudioCommand):
    preloaded_names: List[str]

    def __init__(self, filter_factory: MessageFilterFactoryInterface, task_extractor: TaskExtractor, bitrix_manager: BitrixManager, transcricribe_request_log_dir: str, audio_loader_interface: AudioLoaderInterface):
        super().__init__(filter_factory, audio_loader_interface, task_extractor, transcricribe_request_log_dir, bitrix_manager, "speaker_correction_state_with_preloaded_names")
        self.command_state = "transcribe_audio_with_preloaded_names_command_state"
    
    async def print_end_message(self, message: dict, context: dict, chat: ChatInterface):
        await chat.send_message_to_query("Обработка Google Meet встречи завершена 🚀")

    async def wait_for_audio(self, message: dict, context: dict, chat: ChatInterface):
        await chat.send_message_to_query("⏮️ Отправьте аудиозапись встречи. Если же вы хотите завершить обработку, выполните команду /cancel.")

    def get_conversation_states(self) -> Dict[str, MessageHandler]:
        states = super().get_conversation_states()

        states[self.command_state] += [
            MessageHandler(self.filter_factory.create_filter("command", dict(command="cancel")), self.cancel_command),
            MessageHandler(self.filter_factory.create_filter("all"), self.wait_for_audio)
        ]

        return states