from typing import List, Dict
from src.commands.transcribe_audio_command import TranscribeAudioCommand
from src.commands.audio_loaders.dropbox_audio_loader import DropboxAudioLoader
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager
from src.bitrix.bitrix_manager import BitrixManager
from src.chat_api.chat.chat_interface import ChatInterface
from src.chat_api.message_filters.interfaces.message_filter_factory_interface import MessageFilterFactoryInterface
from src.chat_api.message_handler import MessageHandler
from src.format_corrector import FormatCorrector

class DropboxTranscribeAudioCommand(TranscribeAudioCommand):
    def __init__(self, 
                 filter_factory: MessageFilterFactoryInterface, 
                 dropbox_manager: DropBoxManager, 
                 task_extractor: TaskExtractor, 
                 bitrix_manager: BitrixManager, 
                 transcricribe_request_log_dir: str,
                 format_corrector: FormatCorrector):
        super().__init__(
            filter_factory, 
            DropboxAudioLoader(dropbox_manager), 
            task_extractor, 
            transcricribe_request_log_dir, 
            bitrix_manager, 
            "dropbox_speaker_correction_state", 
            format_corrector
            )

    def get_conversation_states(self) -> Dict[str, MessageHandler]:
        return {
            "entry_point": [
                MessageHandler(self.filter_factory.create_filter("command", dict(command="from_dropbox")), self.handle_command)
            ]
        }