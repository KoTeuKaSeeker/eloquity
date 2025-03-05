from typing import List
from src.commands.transcribe_audio_command import TranscribeAudioCommand
from src.commands.audio_loaders.dropbox_audio_loader import DropboxAudioLoader
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager
from telegram.ext._handlers.basehandler import BaseHandler
from telegram.ext import CommandHandler
from src.bitrix.bitrix_manager import BitrixManager

class DropboxTranscribeAudioCommand(TranscribeAudioCommand):
    def __init__(self, dropbox_manager: DropBoxManager, task_extractor: TaskExtractor, bitrix_manager: BitrixManager, transcricribe_request_log_dir: str):
        super().__init__(DropboxAudioLoader(dropbox_manager), task_extractor, transcricribe_request_log_dir, bitrix_manager)

    def get_telegram_handler(self) -> BaseHandler:
        return CommandHandler('from_dropbox', self.handle_command)