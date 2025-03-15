from typing import List, Dict
from src.commands.transcribe_audio_command import TranscribeAudioCommand
from src.commands.audio_loaders.dropbox_audio_loader import DropboxAudioLoader
from src.task_extractor import TaskExtractor
from src.drop_box_manager import DropBoxManager
from src.bitrix.bitrix_manager import BitrixManager
from src.conversation.conversation_states_manager import ConversationState
from src.chat_api.chat_interface import ChatInterface
from src.chat_api.message_handlers.message_handler_interface import MessageHandlerInterface
from src.chat_api.message_filters.message_filter_interface import MessageFilterInterface

class DropboxTranscribeAudioCommand(TranscribeAudioCommand):
    def __init__(self, dropbox_manager: DropBoxManager, task_extractor: TaskExtractor, bitrix_manager: BitrixManager, transcricribe_request_log_dir: str):
        super().__init__(DropboxAudioLoader(dropbox_manager), task_extractor, transcricribe_request_log_dir, bitrix_manager, ConversationState.dropbox_speaker_correction_state)

    def get_entry_points(self) -> List[MessageHandlerInterface]:
        return [MessageHandlerInterface.from_filter(MessageFilterInterface.from_str("command", dict(command="from_dropbox")), self.handle_command)]