from src.commands.audio_loaders.path_audio_loader import PathAudioLoader
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager
from src.commands.transcribe_audio_with_preloaded_names_command import TranscribeAudioWithPreloadedNamesCommand

class PathTranscribeAudioWithPreloadedNamesCommand(TranscribeAudioWithPreloadedNamesCommand):
    path_audio_loader: PathAudioLoader

    def __init__(self, task_extractor: TaskExtractor, transcricribe_request_log_dir: str):
        self.path_audio_loader = PathAudioLoader()
        super().__init__(task_extractor, transcricribe_request_log_dir, self.path_audio_loader)
    
    def set_audio_path(self, audio_path: str):
        self.path_audio_loader.set_audio_path(audio_path)