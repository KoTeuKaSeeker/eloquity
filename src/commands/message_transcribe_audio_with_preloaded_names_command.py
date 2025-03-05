from src.commands.audio_loaders.message_audio_loader import MessageAudioLoader
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager
from src.commands.audio_loaders.message_audio_loader import MessageAudioLoader
from src.commands.transcribe_audio_with_preloaded_names_command import TranscribeAudioWithPreloadedNamesCommand
from src.bitrix.bitrix_manager import BitrixManager

class MessageTranscribeAudioWithPreloadedNamesCommand(TranscribeAudioWithPreloadedNamesCommand):
    def __init__(self, dropbox: DropBoxManager, task_extractor: TaskExtractor, bitrix_manager: BitrixManager, transcricribe_request_log_dir: str):
        super().__init__(MessageAudioLoader(dropbox), bitrix_manager, task_extractor, transcricribe_request_log_dir)