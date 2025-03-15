import os
import json
import logging
from src.drop_box_manager import DropBoxManager
from src.format_handlers_manager import FormatHandlersManager
from src.commands.audio_loaders.audio_loader_interface import AudioLoaderInterface
from src.exeptions.telegram_exceptions.too_big_file_exception import TooBigFileException
from src.exeptions.telegram_exceptions.telegram_bot_exception import TelegramBotException
from src.exeptions.telegram_exceptions.not_supported_format_exception import NotSupportedFormatException
from src.chat_api.chat_interface import ChatInterface
from src.chat_api.message_handlers.message_handler_interface import MessageHandlerInterface
from src.chat_api.message_filters.message_filter_interface import MessageFilterInterface


class MessageAudioLoader(AudioLoaderInterface):
    dropbox_manager: DropBoxManager

    def __init__(self, dropbox_manager: DropBoxManager):
        self.dropbox_manager = dropbox_manager

    async def load_audio(self, message: dict, message_type: str, context: dict, chat: ChatInterface, json_log: dict = None, request_log_dir: str = "", request_id: int = -1) -> str:
        try:
            request_log_path = os.path.join(request_log_dir, "log.json")
            handlers_manager: FormatHandlersManager = FormatHandlersManager(request_log_dir, request_log_dir, ".wav")
            audio_path = await handlers_manager.load_audio(message, message_type, context, chat)
            return audio_path
        except TooBigFileException as e:
            if json_log is not None:
                json_log["exception"] = "TooBigFileException"
            
            await chat.send_message_to_query(e.open_dropbox_response(context, self.dropbox_manager))

            if json_log is not None:
                with open(request_log_path, "w", encoding="utf-8") as file:
                    json.dump(json_log, file, indent=2, ensure_ascii=False)

            logging.warning(f"Transcription request failed due to 'TooBigFileException'. Request ID: {request_id}")
            return None
        except NotSupportedFormatException as e:
            if json_log is not None:
                json_log["exception"] = "Exception"
            await chat.send_message_to_query(str(TelegramBotException(e)))
            logging.error(f"Transcription request failed due to an not supproted format ({e.not_supported_format}). Request ID: {request_id}")
            return None
        except Exception as e:
            if json_log is not None:
                json_log["exception"] = "Exception"
            await chat.send_message_to_query(str(TelegramBotException(e)))
            logging.error(f"Transcription request failed due to an unknown exception. Request ID: {request_id}")
            return None