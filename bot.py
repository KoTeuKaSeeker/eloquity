from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from pydub import AudioSegment
from huggingface_hub import login
import whisperx
import torch
from huggingface_hub import snapshot_download
from typing import List
from moviepy import VideoFileClip
from src.format_handlers_manager import FormatHandlersManager
from src.audio_transcriber import AudioTranscriber
from src.exeptions.unknown_error_exception import UnknownErrorException

TOKEN = "7851976081:AAFT1jZiwCscWbpXs_L_D_E5p2CF0A_4nYo"
HUGGING_FACE_TOKEN = "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"
BOT_USERNAME = "zebrains_trascriber_bot"
AUDIO_DIR = "audio/"
VIDEO_DIR = "video/"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет. Это бот для анализа аудио и видео сообщений и извлечения из них информации по задаче.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a help command!")


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command!")


async def transcribe_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    handlers_manager: FormatHandlersManager = FormatHandlersManager(AUDIO_DIR, VIDEO_DIR, ".wav")
    try:
        audio_path = await handlers_manager.load_audio(update, context)
    except Exception as e:
        await update.message.reply_text(str(e))
        return

    trancribe_result: AudioTranscriber.TranscribeResult = audio_transcriber.transcript_audio(audio_path)
    os.remove(audio_path)

    message = "\n".join(f"[SPEAKER-{segment.speaker_id}]: {segment.text}" for segment in trancribe_result.segments)
    await update.message.reply_text(message)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")
    await update.message.reply_text(str(UnknownErrorException()))


def app_initialization():
    print("Starting the bot...")
    
    login(HUGGING_FACE_TOKEN)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        compute_type = "float16" if torch.cuda.get_device_capability(0)[0] >= 7 else "float32"
    else:
        compute_type = "float32"

    print("Initialization AI models...")
    audio_transcriber: AudioTranscriber = AudioTranscriber(AudioTranscriber.WisperSize.TINY, "ru", device, compute_type)
    
    print("Initialization the API connection...")
    app = Application.builder().token(TOKEN).build()

    return app, audio_transcriber, device 


if __name__ == "__main__":
    app, audio_transcriber, device = app_initialization()
    print("Initialization is done. Bot ready to work!")

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    
    app.add_handler(MessageHandler(None, transcribe_file))

    app.add_error_handler(error)

    print("Polling...")
    app.run_polling(poll_interval=3)