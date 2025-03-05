from typing import List
from src.commands.transcribe_audio_command import TranscribeAudioCommand
from src.commands.audio_loaders.message_audio_loader import MessageAudioLoader
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager
from telegram.ext._handlers.basehandler import BaseHandler
from telegram.ext import MessageHandler, filters, ConversationHandler, ContextTypes
from telegram import Update
from src.bitrix.bitrix_manager import BitrixManager

class MessageTranscribeAudioCommand(TranscribeAudioCommand):
    def __init__(self, dropbox_manager: DropBoxManager, task_extractor: TaskExtractor, bitrix_manager: BitrixManager, transcricribe_request_log_dir: str):
        super().__init__(MessageAudioLoader(dropbox_manager), task_extractor, transcricribe_request_log_dir, bitrix_manager)
    

            