from src.drop_box_manager import DropBoxManager
from src.commands.audio_loaders.audio_loader_interface import AudioLoaderInterface
from src.exeptions.telegram_exceptions.telegram_bot_exception import TelegramBotException
from src.exeptions.dropbox_exceptions.dropbox_is_empty_exception import DropboxIsEmptyException
from src.chat_api.chat.chat_interface import ChatInterface
from src.chat_api.message_handler import MessageHandler

class DropboxAudioLoader(AudioLoaderInterface):
    dropbox_manager: DropBoxManager

    def __init__(self, dropbox_manager: DropBoxManager):
        self.dropbox_manager = dropbox_manager

    async def load_audio(self, message: dict, context: dict, chat: ChatInterface, json_log: dict = None, request_log_dir: str = "", request_id: int = -1) -> str:
        try:
            audio_path = self.dropbox_manager.load_user_drop(context, chat)
            return audio_path
        except DropboxIsEmptyException as e:
            await chat.send_message_to_query(e.open_dropbox_request(context, self.dropbox_manager))
            return None
        except Exception as e:
            await chat.send_message_to_query(TelegramBotException(e))
            return None