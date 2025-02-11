from src.commands.transcribe_audio_command import TranscribeAudioCommand
from src.commands.audio_loaders.dropbox_audio_loader import DropboxAudioLoader
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager

class DropboxTranscribeAudioCommand(TranscribeAudioCommand):
    def __init__(self, dropbox_manager: DropBoxManager, task_extractor: TaskExtractor, transcricribe_request_log_dir: str):
        super().__init__(DropboxAudioLoader(dropbox_manager), task_extractor, transcricribe_request_log_dir)
