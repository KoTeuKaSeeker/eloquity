from typing import List
from src.commands.transcribe_audio_command import TranscribeAudioCommand
from src.commands.audio_loaders.message_audio_loader import MessageAudioLoader
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager
from src.commands.audio_loaders.audio_loader_interface import AudioLoaderInterface
from telegram.ext._handlers.basehandler import BaseHandler
from telegram.ext import MessageHandler, filters, ConversationHandler
from src.bitrix.bitrix_manager import BitrixManager

class TranscribeAudioWithPreloadedNamesCommand(TranscribeAudioCommand):
    preloaded_names: List[str]

    def __init__(self, task_extractor: TaskExtractor, bitrix_manager: BitrixManager, transcricribe_request_log_dir: str, audio_loader_interface: AudioLoaderInterface):
        super().__init__(audio_loader_interface, task_extractor, transcricribe_request_log_dir, bitrix_manager)
        self.preloaded_names = []

    async def handle_command(self, update, context):
        await super().handle_command(update, context)
        await update.message.reply_text("🚀 Обработка Google Meet беседы завершена.")
        return ConversationHandler.END
    
    def set_preloaded_names(self, preloaded_names: List[str]):
        self.preloaded_names = preloaded_names
    
    def get_preloaded_names(self) -> List[str]:
        return self.preloaded_names