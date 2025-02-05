from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from pydub import AudioSegment
from huggingface_hub import login
import whisperx
import dropbox
import torch
from dotenv import load_dotenv
from huggingface_hub import snapshot_download
from typing import List
from moviepy import VideoFileClip
from src.format_handlers_manager import FormatHandlersManager
from src.audio_transcriber import AudioTranscriber
from src.exeptions.unknown_error_exception import UnknownErrorException
from src.exeptions.not_supported_format_exception import NotSupportedFormatException
from src.exeptions.dropbox_is_empty_exception import DropboxIsEmptyException
from src.exeptions.too_big_file_exception import TooBigFileException
from src.eloquity_ai import EloquityAI
from src.format_handlers_manager import allow_audio_extentions, allow_video_extentions
from src.file_extractors.audio_extractor import AudioExtractor
from src.file_extractors.audio_from_video_extractor import AudioFromVideoExtractor
from src.drop_box_manager import DropBoxManager
import uuid

BOT_USERNAME = "zebrains_trascriber_bot"
AUDIO_DIR = "audio/"
VIDEO_DIR = "video/"
DROPBOX_DIR = "/transcribe_requests/"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет. Это бот для анализа аудио и видео сообщений и извлечения из них информации по задаче.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a help command!")


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command!")

async def from_dropbox_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file_path = drop_box_manager.load_user_drop(update)
        tasks_str = extract_tasks_from_audio_file(file_path)
        await update.message.reply_text(tasks_str)
    except DropboxIsEmptyException as e:
        await update.message.reply_text(e.open_dropbox_request(update, drop_box_manager))
        return
    except Exception as e:
        await update.message.reply_text(e)


def extract_tasks_from_audio_file(audio_path: str):
    trancribe_result: AudioTranscriber.TranscribeResult = audio_transcriber.transcript_audio(audio_path)

    conversation = "\n".join(f"speaker_{segment.speaker_id}: {segment.text}" for segment in trancribe_result.segments)
    tasks_str = eloquity.generate_task_string(conversation)
    return tasks_str


async def transcribe_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update.message.chat.send_action("typing")
    handlers_manager: FormatHandlersManager = FormatHandlersManager(AUDIO_DIR, VIDEO_DIR, ".wav")
    try:
        audio_path = await handlers_manager.load_audio(update, context)
        await update.message.reply_text("⏮️ Файл был успешно загружен. Идёт обработка звука и анализ текста... 🔃")
        update.message.chat.send_action("typing")
    except TooBigFileException as e:
        await update.message.reply_text(e.open_dropbox_response(update, drop_box_manager))
        return
    except Exception as e:
        await update.message.reply_text(str(e))
        return

    task_str = extract_tasks_from_audio_file(audio_path)
    os.remove(audio_path)

    await update.message.reply_text(task_str)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")
    await update.message.reply_text(str(UnknownErrorException()))


def app_initialization():
    print("Starting the bot...")
    
    load_dotenv()
    gptunnel_api_key = os.getenv("GPTUNNEL_API_KEY")
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    hugging_face_token = os.getenv("HUGGING_FACE_TOKEN")
    drop_box_token = os.getenv("DROP_BOX_TOKEN")

    login(hugging_face_token)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        compute_type = "float16" if torch.cuda.get_device_capability(0)[0] >= 7 else "float32"
    else:
        compute_type = "float32"

    print("Initialization AI models...")
    audio_transcriber: AudioTranscriber = AudioTranscriber(AudioTranscriber.WisperSize.TINY, "ru", device, compute_type)
    
    print("Initialization the API connection...")
    app = Application.builder().token(telegram_bot_token).build()
    eloquity = EloquityAI(api_key=gptunnel_api_key)
    drop_box_manager = DropBoxManager(DROPBOX_DIR, AUDIO_DIR, VIDEO_DIR, drop_box_token)

    return app, audio_transcriber, eloquity, drop_box_manager, device 


if __name__ == "__main__":
    app, audio_transcriber, eloquity, drop_box_manager, device = app_initialization()
    print("Initialization is done. Bot ready to work!")

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('from_dropbox', from_dropbox_command))
    
    app.add_handler(MessageHandler(None, transcribe_file))

    app.add_error_handler(error)

    print("Polling...")
    app.run_polling(poll_interval=3)