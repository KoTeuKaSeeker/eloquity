import os
from typing import List
from telegram import Update
from moviepy import VideoFileClip
from src.format_handlers.video_handlers.video_format_handler import VideoFormatHandler
from src.exeptions.unknown_error_exception import UnknownErrorException

class RecognizedVideoFormatHandler(VideoFormatHandler):

    async def load_audio(self, update: Update, context) -> str:
        if update.message.video:
            file = await update.message.video.get_file()
            file_name = update.message.video.file_name or "video.mp4"
            video_ext = os.path.splitext(file_name)[1]
            video_path = os.path.join(self.video_dir, f"{update.message.video.file_id}{video_ext}")
            await file.download_to_drive(video_path)

            audio_path = os.path.join(self.audio_dir, f"temp_{update.message.from_user.id}_audio{self.audio_extention_to_save}")

            try:
                video = VideoFileClip(video_path)
                video.audio.write_audiofile(audio_path, codec="pcm_s16le")
                video.close()

                os.remove(video_path)

                return audio_path
            except Exception as e:
                raise UnknownErrorException()
            finally:
                if os.path.exists(video_path):
                    os.remove(video_path)
        else:
            return None