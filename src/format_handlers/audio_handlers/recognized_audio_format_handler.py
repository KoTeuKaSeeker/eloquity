import os
from telegram import Message
from pydub import AudioSegment
import dropbox
from src.exeptions.unknown_error_exception import UnknownErrorException
from src.format_handlers.audio_handlers.audio_format_handler import AudioFormatHandler
from src.file_extractors.audio_extractor import AudioExtractor
from src.exeptions.telegram_exceptions.too_big_file_exception import TooBigFileException
from telegram.error import BadRequest

class RecognizedAudioFormatHandler(AudioFormatHandler):
    audio_extractor: AudioExtractor

    def __init__(self, audio_dir: str, audio_extention_to_save: str):
        super().__init__(audio_dir, audio_extention_to_save)
        self.audio_extractor = AudioExtractor()

    async def load_audio(self, message: Message) -> str:
        if message.audio or message.voice:
            audio = message.audio or message.voice
            file_id = audio.file_id

            try:
                file = await message.get_bot().get_file(file_id)
            except BadRequest as e:
                if e.message == "File is too big":
                    raise TooBigFileException()
                raise UnknownErrorException()

            file_path = os.path.join(self.audio_dir, f"{file_id}.ogg")
            await file.download_to_drive(file_path)

            changed_extention_path = os.path.splitext(file_path)[0] + self.audio_extention_to_save
            self.audio_extractor.extract_file(file_path, changed_extention_path)
            return changed_extention_path
        else:
            return None
