from src.commands.audio_loaders.message_audio_loader import MessageAudioLoader
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager
from src.commands.audio_loaders.message_audio_loader import MessageAudioLoader
from src.commands.transcribe_audio_with_preloaded_names_command import TranscribeAudioWithPreloadedNamesCommand

class MessageTranscribeAudioWithPreloadedNamesCommand(TranscribeAudioWithPreloadedNamesCommand):
    def __init__(self, dropbox: DropBoxManager, task_extractor: TaskExtractor, transcricribe_request_log_dir: str):
        super().__init__(MessageAudioLoader(dropbox), task_extractor, transcricribe_request_log_dir)