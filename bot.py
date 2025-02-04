from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from pydub import AudioSegment
from huggingface_hub import login
import whisperx
import torch
from huggingface_hub import snapshot_download


TOKEN = "7851976081:AAFT1jZiwCscWbpXs_L_D_E5p2CF0A_4nYo"
BOT_USERNAME = "zebrains_trascriber_bot"
AUDIO_DIR = "audio/"

login("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")

device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cuda":
    compute_type = "float16" if torch.cuda.get_device_capability(0)[0] >= 7 else "float32"
else:
    compute_type = "float32"

model = whisperx.load_model("medium", device, compute_type=compute_type)
diarize_model = whisperx.DiarizationPipeline(device=device)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет. Это бот для анализа аудио и видео сообщений и извлечения из них информации по задаче.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a help command!")


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command!")


def handle_response(text: str) -> str:
    processed: str = text.lower()

    if "hello" in processed:
        return "Hey there!"
    
    if "how are you" in processed:
        return "Good, hbu?"
    
    return "I don't understand what you wrote..."


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f"User ({update.message.chat.id}) in {message_type}: '{text}'")

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print("Bot:", response)
    await update.message.reply_text(response)

async def handle_voice(update: Update, context):
    await handle_audio(update, context)  # Обрабатываем голосовое как аудио


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio = update.message.audio or update.message.voice
    file_id = audio.file_id
    file = await context.bot.get_file(file_id)

    file_path = os.path.join(AUDIO_DIR, f"{file_id}.ogg")
    await file.download_to_drive(file_path)

    mp3_path = file_path.replace(".ogg", ".mp3")
    audio_segment = AudioSegment.from_file(file_path)
    audio_segment.export(mp3_path, format="mp3")

    transcription = model.transcribe(mp3_path)
    diarization = diarize_model(mp3_path)
    result = whisperx.assign_word_speakers(diarization, transcription["segments"])

    os.remove(file_path)
    os.remove(mp3_path)

    texts = []
    for segment in result["segments"]:
        speaker = segment["speaker"]
        text = segment["text"]
        texts.append(f"{speaker}: {text}")

    await update.message.reply_text("\n".join(texts))


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


if __name__ == "__main__":
    print("Starting the bot...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    app.add_error_handler(error)

    print("Polling...")
    app.run_polling(poll_interval=3)







print()  # Выводим распознанный текст
