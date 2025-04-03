import os
from typing import List
import dropbox
from telegram import Message
from moviepy import VideoFileClip
from src.format_handlers.video_handlers.video_format_handler import VideoFormatHandler
from src.file_extractors.audio_from_video_extractor import AudioFromVideoExtractor
from src.exeptions.unknown_error_exception import UnknownErrorException
from src.exeptions.telegram_exceptions.too_big_file_exception import TooBigFileException
from telegram.error import BadRequest

class RecognizedVideoFormatHandler(VideoFormatHandler):
    audio_from_video_extractor: AudioFromVideoExtractor

    def __init__(self, audio_dir: str, video_dir: str, audio_extention_to_save: str = ".wav"):
        super().__init__(audio_dir, video_dir, audio_extention_to_save)
        self.audio_from_video_extractor = AudioFromVideoExtractor()

    async def load_audio(self, message: Message) -> str:
        if message.video:
            try:
                file = await message.video.get_file()
            except BadRequest as e:
                if e.message == "File is too big":
                    raise TooBigFileException()
                else:
                    raise UnknownErrorException()
            file_name = message.video.file_name or "video.mp4"
            video_ext = os.path.splitext(file_name)[1]
            video_path = os.path.join(self.video_dir, f"{message.video.file_id}{video_ext}")
            await file.download_to_drive(video_path)

            audio_path = os.path.join(self.audio_dir, f"{message.video.file_id}{self.audio_extention_to_save}")
            self.audio_from_video_extractor.extract_file(video_path, audio_path)
            return audio_path
        else:
            return None