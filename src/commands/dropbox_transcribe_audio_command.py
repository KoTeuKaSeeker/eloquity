from typing import List
from src.commands.transcribe_audio_command import TranscribeAudioCommand
from src.commands.audio_loaders.dropbox_audio_loader import DropboxAudioLoader
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager
from telegram.ext._handlers.basehandler import BaseHandler
from telegram.ext import CommandHandler

class DropboxTranscribeAudioCommand(TranscribeAudioCommand):
    def __init__(self, dropbox_manager: DropBoxManager, task_extractor: TaskExtractor, transcricribe_request_log_dir: str):
        super().__init__(DropboxAudioLoader(dropbox_manager), task_extractor, transcricribe_request_log_dir)

    def get_telegram_handlers(self) -> List[BaseHandler]:
        return [
            CommandHandler('from_dropbox', self.handle_command)
        ]