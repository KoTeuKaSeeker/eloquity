from typing import List
from src.commands.transcribe_audio_command import TranscribeAudioCommand
from src.commands.audio_loaders.message_audio_loader import MessageAudioLoader
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager
from src.commands.audio_loaders.audio_loader_interface import AudioLoaderInterface
from src.bitrix.bitrix_manager import BitrixManager
from src.chat_api.chat.chat_interface import ChatInterface
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface

class TranscribeAudioWithPreloadedNamesCommand(TranscribeAudioCommand):
    preloaded_names: List[str]

    def __init__(self, filter_factory: MessageFilterFactoryInterface, task_extractor: TaskExtractor, bitrix_manager: BitrixManager, transcricribe_request_log_dir: str, audio_loader_interface: AudioLoaderInterface):
        super().__init__(filter_factory, audio_loader_interface, task_extractor, transcricribe_request_log_dir, bitrix_manager, "speaker_correction_state_with_preloaded_names")

    async def handle_command(self, message: dict, context: dict, chat: ChatInterface):
        await super().handle_command(message, context, chat)
        await chat.send_message_to_query("🚀 Обработка Google Meet беседы завершена.")
        return chat.move_back(context)