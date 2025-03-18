from src.commands.audio_loaders.message_audio_loader import MessageAudioLoader
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager
from src.commands.audio_loaders.message_audio_loader import MessageAudioLoader
from src.commands.transcribe_audio_with_preloaded_names_command import TranscribeAudioWithPreloadedNamesCommand
from src.bitrix.bitrix_manager import BitrixManager
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface

class MessageTranscribeAudioWithPreloadedNamesCommand(TranscribeAudioWithPreloadedNamesCommand):
    def __init__(self, filter_factory: MessageFilterFactoryInterface, dropbox: DropBoxManager, task_extractor: TaskExtractor, bitrix_manager: BitrixManager, transcricribe_request_log_dir: str):
        super().__init__(filter_factory, task_extractor, bitrix_manager, transcricribe_request_log_dir, MessageAudioLoader(dropbox))
        self.speaker_correction_state = "message_speaker_correction_state_with_preloaded_names"