from src.drop_box_manager import DropBoxManager
from src.commands.audio_loaders.audio_loader_interface import AudioLoaderInterface
from src.exeptions.telegram_exceptions.telegram_bot_exception import TelegramBotException
from src.exeptions.dropbox_exceptions.dropbox_is_empty_exception import DropboxIsEmptyException
from src.chat_api.chat_interface import ChatInterface
from src.chat_api.message_handlers.message_handler_interface import MessageHandlerInterface
from src.chat_api.message_filters.message_filter_interface import MessageFilterInterface
import uuid
import os

class TextAudioLoadder(AudioLoaderInterface):
    temp_dir: str

    def __init__(self, temp_dir: str):
        self.temp_dir = temp_dir

    async def load_audio(self, message: dict, message_type: str, context: dict, chat: ChatInterface, json_log: dict = None, request_log_dir: str = "", request_id: int = -1) -> str:
        audio_text = message["audio_text"]

        file_name = str(uuid.uuid4()) + ".txt"
        file_path = os.path.join(self.temp_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(audio_text)
        return file_path