from src.drop_box_manager import DropBoxManager
from src.commands.audio_loaders.audio_loader_interface import AudioLoaderInterface
from src.exeptions.telegram_exceptions.telegram_bot_exception import TelegramBotException
from src.exeptions.dropbox_exceptions.dropbox_is_empty_exception import DropboxIsEmptyException
from src.chat_api.chat_interface import ChatInterface
from src.chat_api.message_handlers.message_handler_interface import MessageHandlerInterface
from src.chat_api.message_filters.message_filter_interface import MessageFilterInterface

class PathAudioLoader(AudioLoaderInterface):
    audio_path_key: str

    def __init__(self, audio_path_key: str = "preloaded_audio_path"):
        self.audio_path_key = audio_path_key

    async def load_audio(self, message: dict, message_type: str, context: dict, chat: ChatInterface, json_log: dict = None, request_log_dir: str = "", request_id: int = -1) -> str:
        return context["user_data"][self.audio_path_key]