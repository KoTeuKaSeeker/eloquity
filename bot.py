import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("speechbrain.utils.quirks").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

import colorlog

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from pydub import AudioSegment
from huggingface_hub import login
import torch
from dotenv import load_dotenv
from huggingface_hub import snapshot_download
from typing import List
from moviepy import VideoFileClip
from src.format_handlers_manager import FormatHandlersManager
from src.transcribers.audio_transcriber import AudioTranscriber
from src.transcribers.sieve_audio_transcriber import SieveAudioTranscriber
from src.transcribers.deepgram_transcriber import DeepgramTranscriber
from src.exeptions.unknown_error_exception import UnknownErrorException
from src.exeptions.not_supported_format_exception import NotSupportedFormatException
from src.exeptions.dropbox_is_empty_exception import DropboxIsEmptyException
from src.exeptions.too_big_file_exception import TooBigFileException
from src.eloquity_ai import EloquityAI
from src.format_handlers_manager import allow_audio_extentions, allow_video_extentions
from src.file_extractors.audio_extractor import AudioExtractor
from src.file_extractors.audio_from_video_extractor import AudioFromVideoExtractor
from src.exeptions.dropbox_refresh_token_exception import DropboxRefreshTokenException
from src.drop_box_manager import DropBoxManager
from src.commands.message_transcribe_audio_command import MessageTranscribeAudioCommand
from src.commands.dropbox_transcribe_audio_command import DropboxTranscribeAudioCommand
from src.task_extractor import TaskExtractor
import uuid
import json



BOT_USERNAME = "zebrains_trascriber_bot"
AUDIO_DIR = "tmp/"
VIDEO_DIR = "tmp/"
DOCX_DIR = "tmp/"
DROPBOX_DIR = "/transcribe_requests/"
DOCX_TEMPLATE_PATH = "docx_templates/default.docx"
LOG_DIR = "logs/"
TRANSCRIBE_REQUEST_LOG_DIR = os.path.join(LOG_DIR, "transcribe_requests")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет. Это бот для анализа аудио и видео сообщений и извлечения из них информации по задаче.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a help command!")


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command!")
    

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")
    await update.message.reply_text(str(UnknownErrorException()))


def load_commands(dbx: DropBoxManager, task_extractor: TaskExtractor):
    commands = {}
    commands[MessageTranscribeAudioCommand] = MessageTranscribeAudioCommand(dbx, task_extractor, TRANSCRIBE_REQUEST_LOG_DIR)
    commands[DropboxTranscribeAudioCommand] = DropboxTranscribeAudioCommand(dbx, task_extractor, TRANSCRIBE_REQUEST_LOG_DIR)

    return commands


def app_initialization():
    logging.info("Starting the bot")
    
    load_dotenv()
    gptunnel_api_key = os.getenv("GPTUNNEL_API_KEY")
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    hugging_face_token = os.getenv("HUGGING_FACE_TOKEN")
    dropbox_app_key = os.getenv("DROPBOX_APP_KEY")
    dropbox_app_secret = os.getenv("DROPBOX_APP_SECRET")
    dropbox_refresh_token = os.getenv("DROPBOX_REFRESH_TOKEN")
    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")

    login(hugging_face_token)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        compute_type = "float16" if torch.cuda.get_device_capability(0)[0] >= 7 else "float32"
    else:
        compute_type = "float32"

    logging.info("Initializing AI models")
    audio_transcriber: DeepgramTranscriber = DeepgramTranscriber(deepgram_api_key)
    
    logging.info("Initializing API connection")
    app = Application.builder().token(telegram_bot_token).build()
    eloquity = EloquityAI(api_key=gptunnel_api_key, model_name='gpt-4o')
    drop_box_manager = DropBoxManager(DROPBOX_DIR, AUDIO_DIR, VIDEO_DIR, dropbox_refresh_token, dropbox_app_key, dropbox_app_secret)

    task_extractor: TaskExtractor = TaskExtractor(audio_transcriber, eloquity, DOCX_TEMPLATE_PATH)

    commands = load_commands(drop_box_manager, task_extractor)

    return app, task_extractor, drop_box_manager, commands, device 


if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
    LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"

    console_handler = colorlog.StreamHandler()

    formatter = colorlog.ColoredFormatter(
    "%(log_color)s" + LOG_FORMAT,
    datefmt=LOG_DATEFMT,
    log_colors={
        'DEBUG': 'blue',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'magenta'
        })
    
    console_handler.setFormatter(formatter)

    os.makedirs(LOG_DIR, exist_ok=True)

    file_handler = logging.FileHandler(os.path.join(LOG_DIR, "app.log"))
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATEFMT))


    logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        console_handler,
        file_handler
    ],
    force=True
    )

    logging.getLogger("sieve._openapi").setLevel(logging.CRITICAL)
    logging.getLogger("sieve").setLevel(logging.CRITICAL)

    app, task_extractor, drop_box_manager, commands, device = app_initialization()
    logging.info("Initialization complete. Bot is ready to work")

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('from_dropbox', commands[DropboxTranscribeAudioCommand].handle_command))
    
    app.add_handler(MessageHandler(filters.AUDIO, commands[MessageTranscribeAudioCommand].handle_command))
    app.add_handler(MessageHandler(filters.VOICE, commands[MessageTranscribeAudioCommand].handle_command))
    app.add_handler(MessageHandler(filters.VIDEO, commands[MessageTranscribeAudioCommand].handle_command))
    app.add_handler(MessageHandler(filters.Document.ALL, commands[MessageTranscribeAudioCommand].handle_command))

    app.add_error_handler(error)

    logging.info("Polling for new events")
    app.run_polling(poll_interval=3)