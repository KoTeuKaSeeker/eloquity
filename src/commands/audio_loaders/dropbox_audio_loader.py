from telegram import Update
from telegram.ext import ContextTypes
from src.drop_box_manager import DropBoxManager
from src.commands.audio_loaders.audio_loader_interface import AudioLoaderInterface
from src.exeptions.telegram_exceptions.telegram_bot_exception import TelegramBotException
from src.exeptions.dropbox_exceptions.dropbox_is_empty_exception import DropboxIsEmptyException

class DropboxAudioLoader(AudioLoaderInterface):
    dropbox_manager: DropBoxManager

    def __init__(self, dropbox_manager: DropBoxManager):
        self.dropbox_manager = dropbox_manager

    async def load_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE, json_log: dict = None, request_log_dir: str = "", request_id: int = -1) -> str:
        try:
            audio_path = self.dropbox_manager.load_user_drop(update)
            return audio_path
        except DropboxIsEmptyException as e:
            await update.message.reply_text(e.open_dropbox_request(update, self.dropbox_manager))
            return None
        except Exception as e:
            await update.message.reply_text(TelegramBotException(e))
            return None