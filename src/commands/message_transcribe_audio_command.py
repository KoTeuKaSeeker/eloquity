from typing import List
from src.commands.transcribe_audio_command import TranscribeAudioCommand
from src.commands.audio_loaders.message_audio_loader import MessageAudioLoader
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager
from src.bitrix.bitrix_manager import BitrixManager
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface
from src.format_corrector import FormatCorrector

class MessageTranscribeAudioCommand(TranscribeAudioCommand):
    def __init__(self, 
                 filter_factory: MessageFilterFactoryInterface, 
                 dropbox_manager: DropBoxManager, 
                 task_extractor: TaskExtractor, 
                 bitrix_manager: BitrixManager, 
                 transcricribe_request_log_dir: str,
                 format_corrector: FormatCorrector):
        super().__init__(
            filter_factory, 
            MessageAudioLoader(dropbox_manager), 
            task_extractor, 
            transcricribe_request_log_dir, 
            bitrix_manager, 
            "message_speaker_correction_state", 
            format_corrector)
    

            