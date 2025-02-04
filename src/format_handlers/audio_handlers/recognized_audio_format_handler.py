import os
from telegram import Update
from pydub import AudioSegment
from src.exeptions.unknown_error_exception import UnknownErrorException
from src.format_handlers.audio_handlers.audio_format_handler import AudioFormatHandler

class RecognizedAudioFormatHandler(AudioFormatHandler):
    async def load_audio(self, update: Update, context) -> str:
        if update.message.audio or update.message.voice:
            try:
                audio = update.message.audio or update.message.voice
                file_id = audio.file_id
                file = await context.bot.get_file(file_id)

                file_path = os.path.join(self.audio_dir, f"{file_id}.ogg")
                await file.download_to_drive(file_path)

                changed_extention_path = os.path.splitext(file_path)[0] + self.audio_extention_to_save
                audio_segment = AudioSegment.from_file(file_path)
                audio_segment.export(changed_extention_path, format=self.audio_extention_to_save.lstrip("."))

                os.remove(file_path)
                return changed_extention_path
            except Exception as e:
                raise UnknownErrorException()
        else:
            return None
