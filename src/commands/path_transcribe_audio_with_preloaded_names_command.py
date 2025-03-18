from src.commands.audio_loaders.path_audio_loader import PathAudioLoader
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager
from src.commands.transcribe_audio_with_preloaded_names_command import TranscribeAudioWithPreloadedNamesCommand
from src.bitrix.bitrix_manager import BitrixManager
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface

class PathTranscribeAudioWithPreloadedNamesCommand(TranscribeAudioWithPreloadedNamesCommand):
    path_audio_loader: PathAudioLoader

    def __init__(self, filter_factory: MessageFilterFactoryInterface, task_extractor: TaskExtractor, bitrix_manager: BitrixManager, transcricribe_request_log_dir: str):
        self.path_audio_loader = PathAudioLoader()
        super().__init__(filter_factory, task_extractor, bitrix_manager, transcricribe_request_log_dir, self.path_audio_loader)
        self.speaker_correction_state = "path_speaker_correction_state_with_preloaded_names"
        self.command_state = "path_transcribe_audio_with_preloaded_names_command_state"